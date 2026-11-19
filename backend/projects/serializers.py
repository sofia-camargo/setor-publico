from rest_framework import serializers
from .models import Project, Tarefa

class TarefaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarefa
        fields = '__all__'

    def validate(self, data):
        if 'data_inicio' in data and 'data_final' in data:
            if data['data_final'] < data['data_inicio']:
                raise serializers.ValidationError({"data_final": "A data final não pode ser anterior à data inicial."})
        return data

class ProjetoSerializer(serializers.ModelSerializer):
    tarefas = TarefaSerializer(many=True, read_only=True, source='tarefa_set')
    
    class Meta:
        model = Project
        fields = '__all__'

    def validate(self, data):
        if 'data_inicio' in data and 'data_fim' in data:
            if data['data_fim'] < data['data_inicio']:
                raise serializers.ValidationError({"data_fim": "A data final não pode ser anterior à data inicial."})
        return data
