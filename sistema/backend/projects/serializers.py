from rest_framework import serializers
from .models import Project, Tarefa


class TarefaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarefa
        fields = '__all__'

    def validate(self, data):
        inicio = data.get('data_inicio', getattr(self.instance, 'data_inicio', None))
        fim = data.get('data_final', getattr(self.instance, 'data_final', None))
        if inicio and fim and fim < inicio:
            raise serializers.ValidationError({
                'data_final': 'A data final não pode ser anterior à data inicial.'
            })
        return data


class ProjetoSerializer(serializers.ModelSerializer):
    tarefas = TarefaSerializer(many=True, read_only=True, source='tarefa_set')
    percentual_conclusao = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def get_percentual_conclusao(self, obj):
        tarefas = obj.tarefa_set.all()
        total = len(tarefas)
        if total == 0:
            return 0
        concluidas = sum(1 for tarefa in tarefas if tarefa.concluida)
        return round((concluidas / total) * 100, 2)

    def validate(self, data):
        inicio = data.get('data_inicio', getattr(self.instance, 'data_inicio', None))
        fim = data.get('data_fim', getattr(self.instance, 'data_fim', None))
        if inicio and fim and fim < inicio:
            raise serializers.ValidationError({
                'data_fim': 'A data final não pode ser anterior à data inicial.'
            })
        return data
