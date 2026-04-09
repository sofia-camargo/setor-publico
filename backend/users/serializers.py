from rest_framework import serializers 
from .models import users, sector 

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = sector
        fields = '__all__' 


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = users       
        fields = '__all__'  