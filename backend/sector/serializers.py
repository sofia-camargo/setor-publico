from rest_framework import serializers
from .models import Sector, Indicador, Atividade

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = '__all__'

class IndicadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Indicador
        fields = '__all__'

class AtividadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atividade
        fields = '__all__'

    def validate_data_cadastro(self, value):
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("A data de cadastro não pode ser no futuro.")
        return value
