from types import SimpleNamespace
from unittest.mock import patch

from datetime import date
from io import BytesIO
from django.core.exceptions import ValidationError
import json

from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from sector.models import Atividade, Indicador, Sector, Empresa, Atendimento
from projects.models import Project, Tarefa
from sector.cnpj import cnpj_check_digits
from sector.cross_indicators import cross_snapshot
from sector.serializers import EmpresaSerializer

from .dashboard import ask_ollama, ask_cross_ollama, dashboard_snapshot, direct_cross_answer
from .insights import ask_insights, raw_analysis_context
from .rag import answer_with_context
from .views import (AssistantQuestionView, DashboardQuestionView, DocumentQuestionView,
                    DocumentStatusView, CrossIndicatorsView, CrossQuestionView,
                    AIAnalysisQuestionView)
from sector.views import AtendimentoCreateListView


class DocumentRoutesTest(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def request_as(self, role, question="Quais são os objetivos?"):
        request = self.factory.post("/api/v1/documentos/perguntar/", {"pergunta": question}, format="json")
        force_authenticate(request, user=SimpleNamespace(is_authenticated=True, nivel_acesso=role))
        return request

    def test_collaborator_cannot_query_documents(self):
        response = DocumentQuestionView.as_view()(self.request_as("Colaborador"))
        self.assertEqual(response.status_code, 403)

    def test_manager_receives_answer_with_sources(self):
        with (
            patch("ai_docs.views.gafia_docs.index_status", return_value=(True, "Índice pronto.", 8)),
            patch("ai_docs.views.get_index", return_value=object()),
            patch("ai_docs.views.gafia_docs.answer", return_value={"resposta": "Texto", "fontes": []}),
        ):
            response = DocumentQuestionView.as_view()(self.request_as("Gestor"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["resposta"], "Texto")

    def test_missing_index_is_reported(self):
        with patch("ai_docs.views.gafia_docs.index_status", return_value=(False, "Reindexe.", 8)):
            response = DocumentQuestionView.as_view()(self.request_as("Administrador"))
        self.assertEqual(response.status_code, 409)

    def test_status_requires_login(self):
        response = DocumentStatusView.as_view()(self.factory.get("/api/v1/documentos/status/"))
        self.assertEqual(response.status_code, 401)


class UnifiedAssistantRoutesTest(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def request_as(self, role, strategic=False, question='O que os dados mostram?'):
        request = self.factory.post('/api/v1/assistente/perguntar/', {
            'pergunta': question,
            'inicio': '2026-09-01', 'fim': '2026-10-01',
        }, format='json')
        force_authenticate(request, user=SimpleNamespace(
            is_authenticated=True, nivel_acesso=role,
            visao_estrategica=strategic, id_setor_id=1,
        ))
        return request

    def test_collaborator_cannot_use_unified_assistant(self):
        response = AssistantQuestionView.as_view()(self.request_as('Colaborador'))
        self.assertEqual(response.status_code, 403)

    def test_secretary_requires_strategic_permission(self):
        response = AssistantQuestionView.as_view()(self.request_as('Secretário', False))
        self.assertEqual(response.status_code, 403)

    def test_manager_uses_single_rag_pipeline(self):
        result = {'resposta': 'Resposta recuperada.', 'fontes': [], 'modo': 'rag'}
        with (
            patch('ai_docs.views.structured_passages', return_value=[{'referencia': 'x'}]),
            patch('ai_docs.views.rank_passages', return_value=[{'referencia': 'x'}]),
            patch('ai_docs.views.gafia_docs.index_status', return_value=(False, 'Ausente', 0)),
            patch('ai_docs.views.answer_with_context', return_value=result) as rag,
        ):
            response = AssistantQuestionView.as_view()(self.request_as('Gestor'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['modo'], 'rag')
        rag.assert_called_once()

    def test_cross_question_has_auditable_fallback_when_model_fails(self):
        request = self.request_as(
            'Administrador', True,
            'Quantas empresas orientadas pelo SEBRAE chegaram ao crédito?',
        )
        fallback = {
            'resposta': 'IC-01: 2 de 3 empresas chegaram ao crédito (66,67%).',
            'fontes': [{'indicador_id': 'IC-01'}],
        }
        with (
            patch('ai_docs.views.structured_passages', return_value=[]),
            patch('ai_docs.views.rank_passages', return_value=[]),
            patch('ai_docs.views.gafia_docs.index_status', return_value=(False, 'Ausente', 0)),
            patch('ai_docs.views.answer_with_context', side_effect=RuntimeError('falha')),
            patch('ai_docs.views.cross_snapshot', return_value=[]),
            patch('ai_docs.views.direct_cross_answer', return_value=fallback),
        ):
            response = AssistantQuestionView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['modo'], 'rag_fallback_auditavel')

    def test_rag_reports_retrieved_source_when_small_model_omits_references(self):
        reply = {'message': {'content': json.dumps({
            'resposta': 'O valor recuperado é 66,67%.', 'referencias': [],
        })}}
        passages = [{
            'referencia': 'IC-01', 'texto': 'IC-01 valor 66,67%.',
            'fonte': {'tipo': 'indicador_cruzado', 'rotulo': 'IC-01'},
        }]
        with patch('ai_docs.rag.urlopen', return_value=BytesIO(json.dumps(reply).encode())):
            result = answer_with_context('Qual o IC-01?', date(2026, 9, 1),
                                         date(2026, 10, 1), passages)
        self.assertEqual(result['fontes'][0]['rotulo'], 'IC-01')

    def test_rag_discards_unknown_reference_without_failing(self):
        reply = {'message': {'content': json.dumps({
            'resposta': 'O contexto recuperado não contém uma contagem autorizada.',
            'referencias': ['IC-01-inexistente'],
        })}}
        passages = [{
            'referencia': 'documento:1', 'texto': 'Trecho autorizado.',
            'fonte': {'tipo': 'documento', 'arquivo': 'manual.pdf'},
        }]
        with patch('ai_docs.rag.urlopen', return_value=BytesIO(json.dumps(reply).encode())):
            result = answer_with_context('Pergunta', date(2026, 9, 1),
                                         date(2026, 10, 1), passages)
        self.assertEqual(result['fontes'][0]['arquivo'], 'manual.pdf')


class DashboardRoutesTest(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def request_as(self, role):
        request = self.factory.post(
            "/api/v1/dashboard/perguntar/",
            {"pergunta": "Quais indicadores tiveram lançamentos?", "inicio": "2026-01-01", "fim": "2026-01-31"},
            format="json",
        )
        force_authenticate(request, user=SimpleNamespace(is_authenticated=True, nivel_acesso=role))
        return request

    def test_collaborator_cannot_query_dashboard(self):
        response = DashboardQuestionView.as_view()(self.request_as("Colaborador"))
        self.assertEqual(response.status_code, 403)

    def test_empty_period_does_not_call_model(self):
        with (
            patch("ai_docs.views.dashboard_snapshot", return_value=[]),
            patch("ai_docs.views.ask_ollama") as model,
        ):
            response = DashboardQuestionView.as_view()(self.request_as("Gestor"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["fontes"], [])
        model.assert_not_called()

    def test_model_sources_are_built_from_authorized_snapshot(self):
        indicators = [{
            "id": 7, "nome": "Atendimentos", "tipo": "Número", "setor": "PAT",
            "soma_lancamentos": "4", "quantidade_lancamentos": 2,
            "historico_mensal": [{"mes": "2026-01", "soma": "4"}],
        }]
        reply = {"message": {"content": json.dumps({
            "resposta": "Foram lançados 4.", "indicadores_usados": [7],
        })}}
        with patch("ai_docs.dashboard.urlopen", return_value=BytesIO(json.dumps(reply).encode())):
            result = ask_ollama("Quantos?", date(2026, 1, 1), date(2026, 1, 31), indicators)
        self.assertEqual(result["fontes"][0]["setor"], "PAT")
        self.assertEqual(result["fontes"][0]["periodo"]["inicio"], "2026-01-01")

    def test_model_cannot_cite_other_indicator(self):
        reply = {"message": {"content": json.dumps({
            "resposta": "Outro indicador.", "indicadores_usados": [999],
        })}}
        with patch("ai_docs.dashboard.urlopen", return_value=BytesIO(json.dumps(reply).encode())):
            with self.assertRaises(RuntimeError):
                ask_ollama("Quantos?", date(2026, 1, 1), date(2026, 1, 31), [{"id": 7}])


class DashboardDataIsolationTest(TestCase):
    def test_manager_only_receives_own_sector(self):
        first = Sector.objects.create(nome="Setor A")
        second = Sector.objects.create(nome="Setor B")
        first_indicator = Indicador.objects.create(nome="A", tipo_dado="Número", id_setor=first)
        second_indicator = Indicador.objects.create(nome="B", tipo_dado="Número", id_setor=second)
        Atividade.objects.create(id_indicador=first_indicator, valor=10, data_cadastro=date(2026, 1, 5))
        Atividade.objects.create(id_indicador=second_indicator, valor=20, data_cadastro=date(2026, 1, 6))
        manager = SimpleNamespace(nivel_acesso="Gestor", id_setor_id=first.id_setor)

        result = dashboard_snapshot(manager, date(2026, 1, 1), date(2026, 1, 31))

        self.assertEqual([item["id"] for item in result], [first_indicator.id_indicador])
        self.assertEqual(result[0]["soma_lancamentos"], "10")


class AIAnalysisTest(TestCase):
    def setUp(self):
        self.first = Sector.objects.create(nome='Setor A')
        self.second = Sector.objects.create(nome='Setor B')
        self.first_indicator = Indicador.objects.create(nome='Atendimentos A', tipo_dado='Número', id_setor=self.first)
        self.second_indicator = Indicador.objects.create(nome='Atendimentos B', tipo_dado='Número', id_setor=self.second)
        self.activity = Atividade.objects.create(id_indicador=self.first_indicator, valor=10,
                                                  data_cadastro=date(2026, 10, 5))
        Atividade.objects.create(id_indicador=self.second_indicator, valor=20,
                                 data_cadastro=date(2026, 10, 6))
        self.project = Project.objects.create(nome='Projeto A', data_inicio=date(2026, 9, 1),
                                               data_fim=date(2026, 10, 31), status_tag='Em andamento',
                                               id_setor=self.first)
        Project.objects.create(nome='Projeto B', data_inicio=date(2026, 9, 1),
                               data_fim=date(2026, 10, 31), status_tag='Em andamento',
                               id_setor=self.second)
        self.task = Tarefa.objects.create(id_projeto=self.project, nome_tarefa='Entrega A',
                                         responsavel_nome='Teste', data_inicio=date(2026, 9, 1),
                                         data_final=date(2026, 10, 20), concluida=False)
        self.manager = SimpleNamespace(nivel_acesso='Gestor', id_setor_id=self.first.pk,
                                       is_authenticated=True)

    def context(self):
        return raw_analysis_context(self.manager, date(2026, 9, 1), date(2026, 10, 31))

    def test_manager_context_contains_only_own_sector_and_no_personal_data(self):
        context = self.context()
        self.assertEqual([item['indicador'] for item in context['lancamentos']], ['Atendimentos A'])
        self.assertEqual([item['nome'] for item in context['projetos']], ['Projeto A'])
        self.assertEqual(context['projetos'][0]['tarefas'][0]['referencia'], f'tarefa:{self.task.pk}')
        self.assertNotIn('responsavel_nome', json.dumps(context))
        self.assertNotIn('cnpj', json.dumps(context))

    def test_model_answer_uses_only_authorized_references(self):
        reference = f'atividade:{self.activity.pk}'
        reply = {'message': {'content': json.dumps({
            'resposta': 'Há um lançamento no período, mas o histórico disponível é insuficiente para apontar uma tendência confiável.',
            'referencias': [reference],
        })}}
        with patch('ai_docs.insights.urlopen', return_value=BytesIO(json.dumps(reply).encode())) as model:
            result = ask_insights('Há tendência?', date(2026, 9, 1), date(2026, 10, 31), self.context())
        self.assertEqual(result['natureza'], 'exploratoria')
        self.assertEqual(result['fontes'][0]['referencia'], reference)

    def test_project_analysis_keeps_task_dates_without_task_names(self):
        reply = {'message': {'content': json.dumps({
            'resposta': 'O prazo do projeto deve ser conferido com as tarefas pendentes; um mês de registros não permite previsão confiável.',
            'referencias': [f'projeto:{self.project.pk}'],
        })}}
        with patch('ai_docs.insights.urlopen', return_value=BytesIO(json.dumps(reply).encode())) as model:
            ask_insights('Há risco de atraso no projeto?', date(2026, 9, 1), date(2026, 10, 31), self.context())
        payload = model.call_args.args[0].data.decode('utf-8')
        self.assertNotIn('Entrega A', payload)
        self.assertIn(f'tarefa:{self.task.pk}', payload)

    def test_model_cannot_cite_another_sector(self):
        reply = {'message': {'content': json.dumps({
            'resposta': 'Setor B tem risco alto.', 'referencias': ['atividade:999'],
        })}}
        with patch('ai_docs.insights.urlopen', return_value=BytesIO(json.dumps(reply).encode())):
            with self.assertRaises(RuntimeError):
                ask_insights('Há risco?', date(2026, 9, 1), date(2026, 10, 31), self.context())

    def test_model_indicator_name_resolves_to_authorized_rows(self):
        reply = {'message': {'content': json.dumps({
            'resposta': 'O indicador possui um lançamento no período, o que é insuficiente para afirmar tendência ou anomalia confiável.',
            'referencias': ['Atendimentos A'],
        })}}
        with patch('ai_docs.insights.urlopen', return_value=BytesIO(json.dumps(reply).encode())):
            result = ask_insights('Há tendência em Atendimentos A?', date(2026, 9, 1),
                                  date(2026, 10, 31), self.context())
        self.assertEqual([item['referencia'] for item in result['fontes']],
                         [f'atividade:{self.activity.pk}'])

    def test_collaborator_cannot_use_analysis(self):
        request = APIRequestFactory().post('/api/v1/analise-ia/perguntar/', {
            'pergunta': 'Há risco?', 'inicio': '2026-09-01', 'fim': '2026-10-31',
        }, format='json')
        force_authenticate(request, user=SimpleNamespace(is_authenticated=True, nivel_acesso='Colaborador'))
        self.assertEqual(AIAnalysisQuestionView.as_view()(request).status_code, 403)


class CrossIndicatorTest(TestCase):
    def setUp(self):
        self.sebrae = Sector.objects.create(nome='SEBRAE Aqui', codigo='SEBRAE')
        self.bank = Sector.objects.create(nome='Banco do Povo', codigo='BP')
        self.pat = Sector.objects.create(nome='PAT', codigo='PAT')
        self.procon = Sector.objects.create(nome='PROCON', codigo='PROCON')
        from users.models import Users
        self.admin = Users.objects.create(matricula='admin-test', nome='Teste', senha_hash='x',
                                          nivel_acesso='Administrador', visao_estrategica=True)

    def company(self, number):
        base = f'ZZZZZZZZ{number:04d}'
        return Empresa.objects.create(cnpj=base + cnpj_check_digits(base),
                                      razao_social=f'Empresa {number}', ramo_atividade='Serviços', bairro='Centro')

    def attendance(self, company, sector, month, day, kind=Atendimento.OUTRO, credit=None, vacancies=None):
        when = date(2026, month, day)
        return Atendimento.objects.create(
            empresa=company, setor=sector, colaborador=self.admin, data_atendimento=when,
            desfecho='Resolvido', tipo=kind, valor_credito=credit,
            data_liberacao=when if credit else None, vagas=vacancies,
            data_abertura_vaga=when if vacancies else None)

    def test_formulas_use_same_company_and_chronological_order(self):
        first = self.company(1)
        self.attendance(first, self.sebrae, 9, 10, Atendimento.SEBRAE)
        self.attendance(first, self.bank, 9, 20, Atendimento.CREDITO, credit=100000)
        self.attendance(first, self.pat, 10, 5, Atendimento.VAGA, vacancies=3)
        second = self.company(2)
        self.attendance(second, self.bank, 9, 10, Atendimento.CREDITO, credit=100000)
        self.attendance(second, self.sebrae, 9, 20, Atendimento.SEBRAE)
        self.attendance(second, self.pat, 9, 5, Atendimento.VAGA, vacancies=7)
        procon_only = self.company(3)
        self.attendance(procon_only, self.procon, 9, 11)

        results = {item['id']: item for item in cross_snapshot(date(2026, 9, 1), date(2026, 10, 26))}
        self.assertEqual((results['IC-01']['numerador'], results['IC-01']['denominador'], results['IC-01']['valor']), (1, 2, '50.00'))
        self.assertEqual((results['IC-02']['vagas_apos_credito'], results['IC-02']['valor']), (3, '1.50'))
        self.assertEqual(results['IC-03']['valor'], 1)
        self.assertEqual((results['IC-04']['numerador'], results['IC-04']['denominador']), (2, 2))
        self.assertFalse(any('cnpj' in item or 'razao_social' in item for item in results.values()))

    def test_zero_denominators_are_not_reported_as_zero_percent(self):
        results = {item['id']: item for item in cross_snapshot(date(2026, 9, 1), date(2026, 10, 26))}
        self.assertIsNone(results['IC-01']['valor'])
        self.assertIsNone(results['IC-02']['valor'])
        self.assertIsNone(results['IC-04']['valor'])

    def test_invalid_cnpj_is_rejected(self):
        with self.assertRaises(ValidationError):
            Empresa.objects.create(cnpj='ZZZZZZZZ000100', razao_social='Teste',
                                   ramo_atividade='Serviços', bairro='Centro')

    def test_company_lookup_reuses_normalized_cnpj_and_hides_procon_sector(self):
        company = self.company(5)
        self.attendance(company, self.procon, 9, 11)
        self.attendance(company, self.sebrae, 9, 12, Atendimento.SEBRAE)
        data = EmpresaSerializer(company).data
        self.assertEqual(data['setores_atendidos'], ['SEBRAE Aqui'])
        formatted = f"{company.cnpj[:2]}.{company.cnpj[2:5]}.{company.cnpj[5:8]}/{company.cnpj[8:12]}-{company.cnpj[12:]}"
        serializer = EmpresaSerializer(data={
            'cnpj': formatted, 'razao_social': 'Outra', 'ramo_atividade': 'Serviços', 'bairro': 'Centro',
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('cnpj', serializer.errors)

    def test_cross_endpoint_requires_individual_permission(self):
        factory = APIRequestFactory()
        request = factory.get('/api/v1/dashboard/cruzados/?inicio=2026-09-01&fim=2026-10-26')
        force_authenticate(request, user=SimpleNamespace(is_authenticated=True, nivel_acesso='Administrador', visao_estrategica=False))
        self.assertEqual(CrossIndicatorsView.as_view()(request).status_code, 403)
        request = factory.get('/api/v1/dashboard/cruzados/?inicio=2026-09-01&fim=2026-10-26')
        force_authenticate(request, user=self.admin)
        self.assertEqual(CrossIndicatorsView.as_view()(request).status_code, 200)

    def test_attendance_cannot_be_registered_in_another_sector(self):
        company = self.company(4)
        request = APIRequestFactory().post('/api/v1/atendimentos/', {
            'empresa': company.pk, 'setor': self.sebrae.pk,
            'data_atendimento': '2026-10-05', 'desfecho': 'Resolvido',
            'tipo': Atendimento.VAGA, 'vagas': 2, 'data_abertura_vaga': '2026-10-05',
        }, format='json')
        # A autenticação usa um usuário real para persistir a autoria.
        self.admin.nivel_acesso = 'Gestor'
        self.admin.id_setor = self.pat
        self.admin.save(update_fields=['nivel_acesso', 'id_setor'])
        force_authenticate(request, user=self.admin)
        response = AtendimentoCreateListView.as_view()(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Atendimento.objects.get(pk=response.data['id']).setor_id, self.pat.pk)

    def test_chat_fallback_uses_computed_values(self):
        indicators = cross_snapshot(date(2026, 9, 1), date(2026, 10, 26))
        result = direct_cross_answer('Qual o IC-01?', date(2026, 9, 1), date(2026, 10, 26), indicators)
        self.assertIn('IC-01', result['resposta'])
        self.assertEqual([source['indicador_id'] for source in result['fontes']], ['IC-01'])
        request = APIRequestFactory().post('/api/v1/dashboard/cruzados/perguntar/', {
            'pergunta': 'Qual o IC-01?', 'inicio': '2026-09-01', 'fim': '2026-10-26',
        }, format='json')
        force_authenticate(request, user=self.admin)
        with patch('ai_docs.views.ask_cross_ollama', side_effect=RuntimeError('offline')):
            response = CrossQuestionView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('IC-01', response.data['resposta'])

    def test_model_cannot_replace_computed_cross_value(self):
        indicators = cross_snapshot(date(2026, 9, 1), date(2026, 10, 26))
        reply = {"message": {"content": json.dumps({
            "resposta": "999 empresas", "indicadores_usados": ["IC-03"],
        })}}
        with patch('ai_docs.dashboard.urlopen', return_value=BytesIO(json.dumps(reply).encode())):
            result = ask_cross_ollama('Qual o IC-03?', date(2026, 9, 1), date(2026, 10, 26), indicators)
        self.assertNotIn('999', result['resposta'])
        self.assertIn('0 empresas', result['resposta'])
