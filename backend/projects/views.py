from rest_framework import generics
from .models import Project, Tarefa
from .serializers import ProjetoSerializer, TarefaSerializer

class ProjetosListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjetoSerializer

class ProjetosRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjetoSerializer

class TarefasListCreateView(generics.ListCreateAPIView):
    queryset = Tarefa.objects.all()
    serializer_class = TarefaSerializer

class TarefasRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tarefa.objects.all()
    serializer_class = TarefaSerializer
