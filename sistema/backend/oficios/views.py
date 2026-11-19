from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Oficios
from .serializers import OficiosSerializer


class OficiosListCreateView(generics.ListCreateAPIView):
    serializer_class = OficiosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        qs = Oficios.objects.select_related('id_usuario', 'id_setor').order_by(
            '-data_oficio', '-id_oficio'
        )
        if usuario.nivel_acesso == 'Administrador':
            return qs
        return qs.filter(id_setor=usuario.id_setor)

    @transaction.atomic
    def perform_create(self, serializer):
        # RF31: usuário e setor sempre vêm do usuário autenticado.
        usuario = self.request.user
        ano = timezone.localdate().year

        # RF30: sequência anual gerada no backend.
        # O lock reduz risco de números repetidos em requisições concorrentes.
        max_num = (
            Oficios.objects.select_for_update()
            .filter(ano=ano)
            .aggregate(maior=Max('numero_sequencial'))['maior']
        )
        numero_sequencial = (max_num or 0) + 1

        serializer.save(
            ano=ano,
            data_oficio=timezone.localdate(),
            numero_sequencial=numero_sequencial,
            id_usuario=usuario,
            id_setor=usuario.id_setor,
        )


class OficiosRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OficiosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        qs = Oficios.objects.select_related('id_usuario', 'id_setor')
        if usuario.nivel_acesso == 'Administrador':
            return qs
        return qs.filter(id_setor=usuario.id_setor)
