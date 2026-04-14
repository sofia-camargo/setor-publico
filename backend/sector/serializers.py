from rest_framework import serializers
# 1. Aqui: Importando com S maiúsculo!
from .models import Sector

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        # 2. Aqui: Apontando para a classe com S maiúsculo!
        model = Sector
        fields = '__all__'