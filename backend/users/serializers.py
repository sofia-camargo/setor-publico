from rest_framework import serializers 
from .models import Users
import re
from rest_framework.exceptions import ValidationError

class UsersSerializer(serializers.ModelSerializer):
    nome_setor = serializers.CharField(source='id_setor.nome', read_only=True)

    class Meta:
        model = Users
        fields = ['id_usuario', 'matricula', 'nome', 'funcao', 'id_setor', 'nome_setor', 'nivel_acesso', 'senha_hash']
        extra_kwargs = {
            'senha_hash': {'write_only': True}
        }

    def validate_senha_hash(self, value):
        if len(value) < 6:
            raise ValidationError("A senha deve ter no mínimo 6 caracteres.")
        if not re.search(r'[A-Z]', value):
            raise ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
        if not re.search(r'[a-z]', value):
            raise ValidationError("A senha deve conter pelo menos uma letra minúscula.")
        if not re.search(r'\d', value):
            raise ValidationError("A senha deve conter pelo menos um número.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError("A senha deve conter pelo menos um caractere especial.")
        return value

    def create(self, validated_data):
        import bcrypt
        if 'senha_hash' in validated_data:
            senha = validated_data['senha_hash']
            validated_data['senha_hash'] = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        import bcrypt
        if 'senha_hash' in validated_data:
            senha = validated_data['senha_hash']
            validated_data['senha_hash'] = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return super().update(instance, validated_data)