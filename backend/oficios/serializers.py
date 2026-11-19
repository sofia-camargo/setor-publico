from rest_framework import serializers
from .models import Oficios

class OficiosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Oficios
        fields = '__all__'
        read_only_fields = ['numero_sequencial', 'ano', 'data_oficio']
