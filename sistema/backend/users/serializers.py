import bcrypt

from rest_framework import serializers

from .models import Users
from .validators import validar_senha


class UsersSerializer(serializers.ModelSerializer):

    nome_setor = serializers.CharField(
        source='id_setor.nome',
        read_only=True
    )

    senha = serializers.CharField(
        write_only=True,
        required=False
    )

    class Meta:
        model = Users

        fields = [
            'id_usuario',
            'matricula',
            'nome',
            'funcao',
            'id_setor',
            'nome_setor',
            'nivel_acesso',
            'visao_estrategica',
            'senha',
            'primeiro_acesso'
        ]

        read_only_fields = [
            'id_usuario',
            'primeiro_acesso'
        ]

    def validate_senha(self, value):
        validar_senha(value)
        return value

    def create(self, validated_data):

        senha = validated_data.pop('senha', None)

        if not senha:
            raise serializers.ValidationError({
                'senha': 'A senha é obrigatória.'
            })

        validar_senha(senha)

        senha_hash = bcrypt.hashpw(
            senha.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        validated_data['senha_hash'] = senha_hash

        # Todo usuário criado pelo administrador
        # começa como primeiro acesso.
        validated_data['primeiro_acesso'] = True

        return Users.objects.create(**validated_data)

    def update(self, instance, validated_data):

        senha = validated_data.pop('senha', None)

        if senha:
            validar_senha(senha)

            instance.senha_hash = bcrypt.hashpw(
                senha.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

        for atributo, valor in validated_data.items():
            setattr(instance, atributo, valor)

        instance.save()

        return instance
