from django.urls import path

from .views import (
    UsersCreateListView,
    UsersRetrieveUpdateDestroyView,
    CustomLoginView,
    AlterarSenhaPropriaView,
    PrimeiroAcessoView,
    RecuperarSenhaPerguntaView,
    RecuperarSenhaVerificarView,
    RecuperarSenhaRedefinirView
)


urlpatterns = [

    # LOGIN
    path(
        'login/',
        CustomLoginView.as_view(),
        name='login'
    ),

    # USUÁRIOS
    path(
        'usuarios/',
        UsersCreateListView.as_view(),
        name='usuarios'
    ),

    path(
        'usuarios/<int:pk>/',
        UsersRetrieveUpdateDestroyView.as_view(),
        name='usuario-detalhe'
    ),

    # PRIMEIRO ACESSO
    path(
        'usuarios/primeiro-acesso/',
        PrimeiroAcessoView.as_view(),
        name='primeiro-acesso'
    ),

    # SENHA
    path(
        'usuarios/alterar-senha/',
        AlterarSenhaPropriaView.as_view(),
        name='alterar-senha'
    ),

    # RECUPERAÇÃO
    path(
        'recuperar-senha/pergunta/',
        RecuperarSenhaPerguntaView.as_view(),
        name='recuperar-pergunta'
    ),

    path(
        'recuperar-senha/verificar/',
        RecuperarSenhaVerificarView.as_view(),
        name='recuperar-verificar'
    ),

    path(
        'recuperar-senha/redefinir/',
        RecuperarSenhaRedefinirView.as_view(),
        name='recuperar-redefinir'
    ),
]