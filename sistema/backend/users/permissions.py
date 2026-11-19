from rest_framework.permissions import BasePermission


class IsAdministrador(BasePermission):
    message = "Apenas administradores podem realizar esta operação."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.nivel_acesso == 'Administrador'
        )


class IsAdministradorOuGestor(BasePermission):
    message = "Você não possui permissão para realizar esta operação."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.nivel_acesso in [
                'Administrador',
                'Gestor'
            ]
        )


class HasStrategicView(BasePermission):
    message = 'Visão estratégica não concedida.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and
                    user.nivel_acesso in ('Administrador', 'Gestor', 'Secretário') and
                    getattr(user, 'visao_estrategica', False))


class CanUseAssistant(BasePermission):
    message = 'Você não possui permissão para usar o assistente.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (
            user.nivel_acesso in ('Administrador', 'Gestor') or
            (user.nivel_acesso == 'Secretário' and getattr(user, 'visao_estrategica', False))
        ))
