from django.urls import path
from . import views

urlpatterns = [
    path('projetos/', views.ProjetosListCreateView.as_view(), name='projetos-list-create'),
    path('projetos/<int:pk>/', views.ProjetosRetrieveUpdateDestroyView.as_view(), name='projetos-detail'),
    path('tarefas/', views.TarefasListCreateView.as_view(), name='tarefas-list-create'),
    path('tarefas/<int:pk>/', views.TarefasRetrieveUpdateDestroyView.as_view(), name='tarefas-detail'),
]
