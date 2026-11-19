from rest_framework import generics
from .models import Users, HistoricoSenhas
from .serializers import UsersSerializer

class UsersCreateListView(generics.ListCreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

class UsersRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer    

import bcrypt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated

class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        matricula = request.data.get('matricula')
        senha = request.data.get('senha')

        if not matricula or not senha:
            return Response({'error': 'Matrícula e senha são obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Users.objects.get(matricula=matricula)
            if bcrypt.checkpw(senha.encode('utf-8'), user.senha_hash.encode('utf-8')):
                refresh = RefreshToken()
                refresh['user_id'] = user.id_usuario
                return Response({
                    'access': str(refresh.access_token),
                    'user': {
                        'id_usuario': user.id_usuario,
                        'nome': user.nome,
                        'nivel_acesso': user.nivel_acesso,
                        'id_setor': user.id_setor.id_setor if user.id_setor else None
                    }
                })
            else:
                return Response({'error': 'Credenciais inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
        except Users.DoesNotExist:
            return Response({'error': 'Credenciais inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

class AlterarSenhaPropriaView(APIView):
    # permission_classes = [IsAuthenticated] # Temporarily AllowAny for tests if needed, but keeping simple JWT
    permission_classes = [AllowAny] 
    
    def post(self, request):
        user_id = request.data.get('user_id')
        senha_atual = request.data.get('senha_atual')
        nova_senha = request.data.get('nova_senha')
        
        try:
            user = Users.objects.get(id_usuario=user_id)
            if not bcrypt.checkpw(senha_atual.encode('utf-8'), user.senha_hash.encode('utf-8')):
                return Response({'error': 'Senha atual incorreta'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = UsersSerializer(user, data={'senha_hash': nova_senha}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Senha alterada com sucesso'})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Users.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

class RedefinirSenhaAdminView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        user_id_alvo = request.data.get('user_id_alvo')
        user_id_admin = request.data.get('user_id_admin')
        nova_senha = request.data.get('nova_senha')
        
        try:
            alvo = Users.objects.get(id_usuario=user_id_alvo)
            admin = Users.objects.get(id_usuario=user_id_admin)
            
            # RN03 - Gestor apenas do seu setor
            if admin.nivel_acesso == 'Gestor' and alvo.id_setor != admin.id_setor:
                return Response({'error': 'Gestor não tem permissão para alterar senha deste setor.'}, status=status.HTTP_403_FORBIDDEN)
                
            serializer = UsersSerializer(alvo, data={'senha_hash': nova_senha}, partial=True)
            if serializer.is_valid():
                serializer.save()
                # Logar a alteracao
                HistoricoSenhas.objects.create(id_usuario=alvo, id_responsavel=admin)
                return Response({'message': 'Senha redefinida com sucesso'})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Users.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)