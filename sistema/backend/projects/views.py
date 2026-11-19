from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Project, Tarefa
from .serializers import ProjetoSerializer, TarefaSerializer


class ProjetosListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjetoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        qs = Project.objects.prefetch_related('tarefa_set').all()
        if usuario.nivel_acesso == 'Administrador':
            return qs
        return qs.filter(id_setor=usuario.id_setor)

    def perform_create(self, serializer):
        usuario = self.request.user
        if usuario.nivel_acesso == 'Administrador':
            serializer.save()
        else:
            serializer.save(id_setor=usuario.id_setor)


class ProjetosRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjetoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        qs = Project.objects.prefetch_related('tarefa_set').all()
        if usuario.nivel_acesso == 'Administrador':
            return qs
        return qs.filter(id_setor=usuario.id_setor)


class TarefasListCreateView(generics.ListCreateAPIView):
    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        qs = Tarefa.objects.select_related('id_projeto').all()
        if usuario.nivel_acesso == 'Administrador':
            return qs
        return qs.filter(id_projeto__id_setor=usuario.id_setor)

    def perform_create(self, serializer):
        projeto = serializer.validated_data['id_projeto']
        usuario = self.request.user
        if (
            usuario.nivel_acesso != 'Administrador'
            and projeto.id_setor_id != usuario.id_setor_id
        ):
            raise PermissionDenied('Você só pode cadastrar tarefas em projetos do seu setor.')
        serializer.save()


class TarefasRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        qs = Tarefa.objects.select_related('id_projeto').all()
        if usuario.nivel_acesso == 'Administrador':
            return qs
        return qs.filter(id_projeto__id_setor=usuario.id_setor)
