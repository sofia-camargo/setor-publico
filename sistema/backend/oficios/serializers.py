from rest_framework import serializers
from .models import Oficios


class OficiosSerializer(serializers.ModelSerializer):
    nome_usuario = serializers.CharField(source='id_usuario.nome', read_only=True)
    nome_setor = serializers.CharField(source='id_setor.nome', read_only=True)

    class Meta:
        model = Oficios
        fields = [
            'id_oficio', 'numero_sequencial', 'ano', 'assunto', 'data_oficio',
            'id_usuario', 'nome_usuario', 'id_setor', 'nome_setor'
        ]
        # RF30/RF31/RN12: estes dados são definidos pelo servidor.
        read_only_fields = [
            'id_oficio', 'numero_sequencial', 'ano', 'data_oficio',
            'id_usuario', 'nome_usuario', 'id_setor', 'nome_setor'
        ]
