from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Sector, Indicador, Atividade, Empresa, Atendimento
from .serializers import SectorSerializer, IndicadorSerializer, AtividadeSerializer, EmpresaSerializer, AtendimentoSerializer
from .cnpj import normalize_cnpj


class SectorCreateListView(generics.ListCreateAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [IsAuthenticated]


class SectorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [IsAuthenticated]


class IndicadorCreateListView(generics.ListCreateAPIView):
    serializer_class = IndicadorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        qs = Indicador.objects.all()
        if usuario.nivel_acesso == 'Administrador':
            return qs
        return qs.filter(id_setor=usuario.id_setor)

    def perform_create(self, serializer):
        usuario = self.request.user
        if usuario.nivel_acesso == 'Administrador':
            serializer.save()
        else:
            serializer.save(id_setor=usuario.id_setor)


class AtividadeCreateListView(generics.ListCreateAPIView):
    serializer_class = AtividadeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        qs = Atividade.objects.select_related('id_indicador', 'id_usuario').order_by('-data_cadastro')
        if usuario.nivel_acesso == 'Administrador':
            return qs
        return qs.filter(id_indicador__id_setor=usuario.id_setor)

    def perform_create(self, serializer):
        # O responsável pelo lançamento é sempre o usuário autenticado.
        serializer.save(id_usuario=self.request.user)


class AtividadeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AtividadeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        qs = Atividade.objects.select_related('id_indicador', 'id_usuario')
        if usuario.nivel_acesso == 'Administrador':
            return qs
        return qs.filter(id_indicador__id_setor=usuario.id_setor)


class EmpresaCreateListView(generics.ListCreateAPIView):
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cnpj = self.request.query_params.get('cnpj')
        if not cnpj:
            return Empresa.objects.none()
        return Empresa.objects.filter(cnpj=normalize_cnpj(cnpj))


class AtendimentoCreateListView(generics.ListCreateAPIView):
    serializer_class = AtendimentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Atendimento.objects.select_related('empresa', 'setor', 'colaborador')
        if self.request.user.nivel_acesso == 'Administrador':
            return qs
        return qs.filter(setor_id=self.request.user.id_setor_id)

    def perform_create(self, serializer):
        try:
            serializer.save(colaborador=self.request.user)
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)
