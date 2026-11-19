from django.urls import path
from .views import (
    SectorCreateListView, 
    SectorRetrieveUpdateDestroyView, 
    IndicadorCreateListView, 
    AtividadeCreateListView
)

urlpatterns = [
    path('setores/', SectorCreateListView.as_view(), name='sector-create-list'),
    path('setores/<int:pk>/', SectorRetrieveUpdateDestroyView.as_view(), name='sector-detail-view'),
    path('indicadores/', IndicadorCreateListView.as_view(), name='indicador-create-list'),
    path('atividades/', AtividadeCreateListView.as_view(), name='atividade-create-list'),
]