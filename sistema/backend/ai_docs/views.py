"""Acesso autenticado do SIGDEI ao índice documental local do GAFIA."""

import logging
import sys
import threading
from pathlib import Path

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsAdministradorOuGestor, HasStrategicView, CanUseAssistant
from .dashboard import ask_ollama, ask_cross_ollama, direct_cross_answer, dashboard_snapshot, parse_period
from sector.cross_indicators import cross_snapshot
from .insights import ask_insights, ollama_status, raw_analysis_context
from .rag import answer_with_context, local_nlp_answer, rag_status, rank_passages, structured_passages

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import gafia_docs  # noqa: E402

logger = logging.getLogger(__name__)
query_lock = threading.Lock()
loaded_index = None
loaded_manifest = None


def get_index():
    global loaded_index, loaded_manifest
    manifest = (gafia_docs.INDEX_DIR / "manifest.json").read_bytes()
    if loaded_index is None or loaded_manifest != manifest:
        loaded_index = gafia_docs.load_index()
        loaded_manifest = manifest
    return loaded_index


class AssistantStatusView(APIView):
    permission_classes = [IsAuthenticated, CanUseAssistant]

    def get(self, request):
        return Response(rag_status(gafia_docs.index_status()))


class AssistantQuestionView(APIView):
    permission_classes = [IsAuthenticated, CanUseAssistant]

    def post(self, request):
        question = request.data.get('pergunta') if isinstance(request.data, dict) else None
        if not isinstance(question, str) or not question.strip() or len(question) > gafia_docs.MAX_QUESTION_LENGTH:
            return Response({'erro': 'Informe uma pergunta de até 2000 caracteres.'}, status=400)
        try:
            start, end = parse_period(request.data.get('inicio'), request.data.get('fim'))
            passages = rank_passages(question, structured_passages(request.user, start, end))
        except ValueError as exc:
            return Response({'erro': str(exc)}, status=400)

        ready, _, _ = gafia_docs.index_status()
        if ready:
            try:
                with query_lock:
                    passages.extend(gafia_docs.retrieve(get_index(), question, top_k=4))
            except Exception:
                logger.exception('Falha na recuperação de trechos documentais do RAG')
        try:
            return Response(answer_with_context(question.strip(), start, end, passages))
        except RuntimeError:
            logger.exception('Falha ao consultar o Assistente RAG')
            if getattr(request.user, 'visao_estrategica', False):
                fallback = direct_cross_answer(
                    question.strip(), start, end, cross_snapshot(start, end)
                )
                if fallback['fontes']:
                    fallback['modo'] = 'rag_fallback_auditavel'
                    return Response(fallback)
            if passages:
                return Response(local_nlp_answer(question.strip(), start, end, passages, user=request.user))
            return Response({'erro': 'O modelo local não respondeu. Confira se o Ollama está em execução.'}, status=503)


class DocumentStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdministradorOuGestor]

    def get(self, request):
        ready, message, count = gafia_docs.index_status()
        return Response({"pronto": ready, "mensagem": message, "arquivos": count})


class DocumentQuestionView(APIView):
    permission_classes = [IsAuthenticated, IsAdministradorOuGestor]

    def post(self, request):
        question = request.data.get("pergunta") if isinstance(request.data, dict) else None
        if not isinstance(question, str) or not question.strip() or len(question) > gafia_docs.MAX_QUESTION_LENGTH:
            return Response({"erro": "Informe uma pergunta de até 2000 caracteres."}, status=400)

        ready, message, _ = gafia_docs.index_status()
        if not ready:
            return Response({"erro": message}, status=409)

        try:
            with query_lock:
                result = gafia_docs.answer(get_index(), question)
            return Response(result)
        except Exception:
            logger.exception("Falha ao consultar o assistente documental")
            return Response({"erro": "O modelo local não respondeu. Confira se o Ollama está em execução."}, status=503)


class DashboardQuestionView(APIView):
    permission_classes = [IsAuthenticated, IsAdministradorOuGestor]

    def post(self, request):
        question = request.data.get("pergunta") if isinstance(request.data, dict) else None
        if not isinstance(question, str) or not question.strip() or len(question) > 1000:
            return Response({"erro": "Informe uma pergunta de até 1000 caracteres."}, status=400)
        try:
            start, end = parse_period(request.data.get("inicio"), request.data.get("fim"))
            indicators = dashboard_snapshot(request.user, start, end)
        except ValueError as exc:
            return Response({"erro": str(exc)}, status=400)

        if not indicators:
            return Response({
                "resposta": "Não há lançamentos de indicadores disponíveis para você nesse período.",
                "fontes": [],
            })
        try:
            return Response(ask_ollama(question.strip(), start, end, indicators))
        except RuntimeError:
            logger.exception("Falha ao consultar o assistente do dashboard")
            return Response({"erro": "O modelo local não respondeu. Confira se o Ollama está em execução."}, status=503)


class CrossIndicatorsView(APIView):
    permission_classes = [IsAuthenticated, HasStrategicView]

    def get(self, request):
        try:
            start, end = parse_period(request.query_params.get('inicio'), request.query_params.get('fim'))
        except ValueError as exc:
            return Response({"erro": str(exc)}, status=400)
        return Response({"periodo": {"inicio": start.isoformat(), "fim": end.isoformat()},
                         "indicadores": cross_snapshot(start, end)})


class CrossQuestionView(APIView):
    permission_classes = [IsAuthenticated, HasStrategicView]

    def post(self, request):
        question = request.data.get('pergunta') if isinstance(request.data, dict) else None
        if not isinstance(question, str) or not question.strip() or len(question) > 1000:
            return Response({"erro": "Informe uma pergunta de até 1000 caracteres."}, status=400)
        try:
            start, end = parse_period(request.data.get('inicio'), request.data.get('fim'))
        except ValueError as exc:
            return Response({"erro": str(exc)}, status=400)
        indicators = cross_snapshot(start, end)
        try:
            return Response(ask_cross_ollama(question.strip(), start, end, indicators))
        except RuntimeError:
            logger.warning('Modelo indisponível; resposta direta para indicadores cruzados')
            return Response(direct_cross_answer(question.strip(), start, end, indicators))


class AIAnalysisStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdministradorOuGestor]

    def get(self, request):
        return Response(ollama_status())


class AIAnalysisQuestionView(APIView):
    permission_classes = [IsAuthenticated, IsAdministradorOuGestor]

    def post(self, request):
        question = request.data.get('pergunta') if isinstance(request.data, dict) else None
        if not isinstance(question, str) or not question.strip() or len(question) > 1000:
            return Response({'erro': 'Informe uma pergunta de até 1000 caracteres.'}, status=400)
        try:
            start, end = parse_period(request.data.get('inicio'), request.data.get('fim'))
            context = raw_analysis_context(request.user, start, end)
        except ValueError as exc:
            return Response({'erro': str(exc)}, status=400)
        if not any(context.values()):
            return Response({'resposta': 'Não há registros autorizados nesse período para analisar.',
                             'fontes': [], 'natureza': 'exploratoria'})
        try:
            return Response(ask_insights(question.strip(), start, end, context))
        except RuntimeError:
            logger.exception('Falha na análise exploratória local')
            return Response({'erro': 'O modelo Ollama não respondeu à análise. Confira se o modelo está ativo.'}, status=503)
