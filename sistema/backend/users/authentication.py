from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from users.models import Users


class CustomJWTAuthentication(JWTAuthentication):

    def get_user(self, validated_token):

        user_id = validated_token.get('user_id')

        if not user_id:
            raise AuthenticationFailed(
                'Token inválido.',
                code='invalid_token'
            )

        try:
            return Users.objects.get(
                id_usuario=user_id
            )

        except Users.DoesNotExist:
            raise AuthenticationFailed(
                'Usuário não encontrado.',
                code='user_not_found'
            )