from django.urls import path

from .views import (AssistantQuestionView, AssistantStatusView, DashboardQuestionView,
                    DocumentQuestionView, DocumentStatusView, CrossIndicatorsView,
                    CrossQuestionView, AIAnalysisStatusView, AIAnalysisQuestionView)

urlpatterns = [
    path("assistente/status/", AssistantStatusView.as_view(), name="assistente-status"),
    path("assistente/perguntar/", AssistantQuestionView.as_view(), name="assistente-perguntar"),
    path("documentos/status/", DocumentStatusView.as_view(), name="documentos-status"),
    path("documentos/perguntar/", DocumentQuestionView.as_view(), name="documentos-perguntar"),
    path("dashboard/perguntar/", DashboardQuestionView.as_view(), name="dashboard-perguntar"),
    path("dashboard/cruzados/", CrossIndicatorsView.as_view(), name="dashboard-cruzados"),
    path("dashboard/cruzados/perguntar/", CrossQuestionView.as_view(), name="dashboard-cruzados-perguntar"),
    path("analise-ia/status/", AIAnalysisStatusView.as_view(), name="analise-ia-status"),
    path("analise-ia/perguntar/", AIAnalysisQuestionView.as_view(), name="analise-ia-perguntar"),
]
