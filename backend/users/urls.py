from django.urls import path
from .views import UsersCreateListView, UsersRetrieveUpdateDestroyView, CustomLoginView, AlterarSenhaPropriaView, RedefinirSenhaAdminView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='custom_login'),
    path('usuarios/', UsersCreateListView.as_view(), name='users-create-list'),
    path('usuarios/<int:pk>/', UsersRetrieveUpdateDestroyView.as_view(), name='users-detail-view'),
    path('usuarios/alterar-senha/', AlterarSenhaPropriaView.as_view(), name='users-alterar-senha'),
    path('usuarios/redefinir-senha/', RedefinirSenhaAdminView.as_view(), name='users-redefinir-senha'),
]