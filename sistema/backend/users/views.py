import bcrypt

from django.core import signing

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Users
from .serializers import UsersSerializer
from .permissions import IsAdministrador
from .validators import validar_senha


# =========================================================
# USUÁRIOS
# =========================================================


class UsersCreateListView(generics.ListCreateAPIView):

    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        usuario = self.request.user

        # Administrador visualiza todos
        if usuario.nivel_acesso == 'Administrador':
            return Users.objects.all()

        # Gestor visualiza apenas seu setor
        if usuario.nivel_acesso == 'Gestor':
            return Users.objects.filter(
                id_setor=usuario.id_setor
            )

        # Colaborador visualiza apenas ele mesmo
        return Users.objects.filter(
            id_usuario=usuario.id_usuario
        )

    def create(self, request, *args, **kwargs):

        # RN01
        if request.user.nivel_acesso != 'Administrador':

            return Response(
                {
                    'error':
                    'Apenas administradores podem cadastrar usuários.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(
            request,
            *args,
            **kwargs
        )


class UsersRetrieveUpdateDestroyView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        if usuario.nivel_acesso == 'Administrador':
            return Users.objects.all()
        return Users.objects.filter(id_usuario=usuario.id_usuario)

    def update(self, request, *args, **kwargs):
        alvo = self.get_object()

        # RN03: senha nunca pode ser alterada pela rota genérica de usuários.
        # O próprio usuário usa /usuarios/alterar-senha/ ou a recuperação.
        if 'senha' in request.data or 'senha_hash' in request.data:
            return Response(
                {'error': 'A senha só pode ser alterada pelo próprio usuário.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Não administradores podem editar somente dados básicos do próprio perfil.
        if request.user.nivel_acesso != 'Administrador':
            permitidos = {'nome', 'funcao'}
            proibidos = set(request.data.keys()) - permitidos
            if proibidos:
                return Response(
                    {'error': 'Você não tem permissão para alterar estes dados.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):

        # RN01
        if request.user.nivel_acesso != 'Administrador':

            return Response(
                {
                    'error':
                    'Apenas administradores podem excluir usuários.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        usuario = self.get_object()

        # Impede administrador de excluir a si próprio
        if usuario.id_usuario == request.user.id_usuario:

            return Response(
                {
                    'error':
                    'Você não pode excluir seu próprio usuário.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().destroy(
            request,
            *args,
            **kwargs
        )


# =========================================================
# LOGIN
# =========================================================


class CustomLoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        matricula = request.data.get('matricula')
        senha = request.data.get('senha')

        if not matricula or not senha:

            return Response(
                {
                    'error':
                    'Matrícula e senha são obrigatórios.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            user = Users.objects.get(
                matricula=matricula
            )

        except Users.DoesNotExist:

            return Response(
                {
                    'error':
                    'Credenciais inválidas.'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not bcrypt.checkpw(
            senha.encode('utf-8'),
            user.senha_hash.encode('utf-8')
        ):

            return Response(
                {
                    'error':
                    'Credenciais inválidas.'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken()

        refresh['user_id'] = user.id_usuario

        return Response({

            'access': str(refresh.access_token),

            'refresh': str(refresh),

            'user': {

                'id_usuario':
                    user.id_usuario,

                'nome':
                    user.nome,

                'matricula':
                    user.matricula,

                'nivel_acesso':
                    user.nivel_acesso,

                'visao_estrategica':
                    user.visao_estrategica,

                'id_setor':
                    user.id_setor.id_setor
                    if user.id_setor
                    else None,

                'primeiro_acesso':
                    user.primeiro_acesso
            }
        })


# =========================================================
# PRIMEIRO ACESSO
# =========================================================


class PrimeiroAcessoView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user

        if not user.primeiro_acesso:

            return Response(
                {
                    'error':
                    'O primeiro acesso deste usuário já foi realizado.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        pergunta = request.data.get(
            'pergunta_seguranca'
        )

        resposta = request.data.get(
            'resposta_seguranca'
        )

        nova_senha = request.data.get(
            'nova_senha'
        )

        if not pergunta or not resposta or not nova_senha:

            return Response(
                {
                    'error':
                    'Pergunta, resposta e nova senha são obrigatórias.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(pergunta.strip()) < 5:

            return Response(
                {
                    'error':
                    'Informe uma pergunta de segurança válida.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(resposta.strip()) < 2:

            return Response(
                {
                    'error':
                    'Informe uma resposta válida.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            validar_senha(nova_senha)

        except Exception as erro:

            detalhe = getattr(
                erro,
                'detail',
                str(erro)
            )

            return Response(
                {
                    'error': detalhe
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        resposta_normalizada = (
            resposta.strip().lower()
        )

        resposta_hash = bcrypt.hashpw(
            resposta_normalizada.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        nova_senha_hash = bcrypt.hashpw(
            nova_senha.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        user.pergunta_seguranca = pergunta.strip()

        user.resposta_seguranca_hash = (
            resposta_hash
        )

        user.senha_hash = nova_senha_hash

        user.primeiro_acesso = False

        user.save()

        return Response({
            'message':
            'Primeiro acesso configurado com sucesso.'
        })


# =========================================================
# ALTERAÇÃO DA PRÓPRIA SENHA
# =========================================================


class AlterarSenhaPropriaView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user

        senha_atual = request.data.get(
            'senha_atual'
        )

        nova_senha = request.data.get(
            'nova_senha'
        )

        if not senha_atual or not nova_senha:

            return Response(
                {
                    'error':
                    'Senha atual e nova senha são obrigatórias.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not bcrypt.checkpw(
            senha_atual.encode('utf-8'),
            user.senha_hash.encode('utf-8')
        ):

            return Response(
                {
                    'error':
                    'Senha atual incorreta.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UsersSerializer(
            user,
            data={
                'senha': nova_senha
            },
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response({
                'message':
                'Senha alterada com sucesso.'
            })

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# =========================================================
# RECUPERAÇÃO DE SENHA
# =========================================================


class RecuperarSenhaPerguntaView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        matricula = request.data.get(
            'matricula'
        )

        if not matricula:

            return Response(
                {
                    'error':
                    'Informe a matrícula.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            user = Users.objects.get(
                matricula=matricula
            )

        except Users.DoesNotExist:

            return Response(
                {
                    'error':
                    'Usuário não encontrado.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if (
            not user.pergunta_seguranca
            or not user.resposta_seguranca_hash
        ):

            return Response(
                {
                    'error':
                    'Este usuário ainda não cadastrou uma pergunta de segurança.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'pergunta':
                user.pergunta_seguranca
        })


class RecuperarSenhaVerificarView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        matricula = request.data.get(
            'matricula'
        )

        resposta = request.data.get(
            'resposta'
        )

        if not matricula or not resposta:

            return Response(
                {
                    'error':
                    'Matrícula e resposta são obrigatórias.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            user = Users.objects.get(
                matricula=matricula
            )

        except Users.DoesNotExist:

            return Response(
                {
                    'error':
                    'Dados inválidos.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.resposta_seguranca_hash:

            return Response(
                {
                    'error':
                    'Pergunta de segurança não cadastrada.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        resposta_normalizada = (
            resposta.strip().lower()
        )

        correta = bcrypt.checkpw(
            resposta_normalizada.encode('utf-8'),
            user.resposta_seguranca_hash.encode(
                'utf-8'
            )
        )

        if not correta:

            return Response(
                {
                    'error':
                    'Resposta incorreta.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        token = signing.dumps({
            'user_id': user.id_usuario,
            'tipo': 'recuperacao_senha'
        })

        return Response({
            'message':
                'Resposta verificada com sucesso.',

            'token':
                token
        })


class RecuperarSenhaRedefinirView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        token = request.data.get(
            'token'
        )

        nova_senha = request.data.get(
            'nova_senha'
        )

        if not token or not nova_senha:

            return Response(
                {
                    'error':
                    'Token e nova senha são obrigatórios.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            dados = signing.loads(
                token,
                max_age=600
            )

        except signing.SignatureExpired:

            return Response(
                {
                    'error':
                    'O prazo para recuperação expirou.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except signing.BadSignature:

            return Response(
                {
                    'error':
                    'Token de recuperação inválido.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if dados.get('tipo') != 'recuperacao_senha':

            return Response(
                {
                    'error':
                    'Token inválido.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            user = Users.objects.get(
                id_usuario=dados.get('user_id')
            )

        except Users.DoesNotExist:

            return Response(
                {
                    'error':
                    'Usuário não encontrado.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UsersSerializer(
            user,
            data={
                'senha': nova_senha
            },
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response({
                'message':
                    'Senha redefinida com sucesso.'
            })

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
