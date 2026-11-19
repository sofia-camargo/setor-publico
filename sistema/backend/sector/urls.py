from django.urls import path
from .views import (
    SectorCreateListView,
    SectorRetrieveUpdateDestroyView,
    IndicadorCreateListView,
    AtividadeCreateListView,
    AtividadeRetrieveUpdateDestroyView,
    EmpresaCreateListView,
    AtendimentoCreateListView,
)

urlpatterns = [
    path('empresas/', EmpresaCreateListView.as_view(), name='empresa-create-list'),
    path('atendimentos/', AtendimentoCreateListView.as_view(), name='atendimento-create-list'),
    path('setores/', SectorCreateListView.as_view(), name='sector-create-list'),
    path('setores/<int:pk>/', SectorRetrieveUpdateDestroyView.as_view(), name='sector-detail-view'),
    path('indicadores/', IndicadorCreateListView.as_view(), name='indicador-create-list'),
    path('atividades/', AtividadeCreateListView.as_view(), name='atividade-create-list'),
    path('atividades/<int:pk>/', AtividadeRetrieveUpdateDestroyView.as_view(), name='atividade-detail'),
]
