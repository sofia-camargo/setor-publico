from datetime import date
from rest_framework import serializers
from django.db.models import Sum
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Sector, Indicador, Atividade, Empresa, Atendimento
from .cnpj import normalize_cnpj, validate_cnpj


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = '__all__'


class IndicadorSerializer(serializers.ModelSerializer):
    valor_total = serializers.SerializerMethodField()

    class Meta:
        model = Indicador
        fields = ['id_indicador', 'id_setor', 'nome', 'tipo_dado', 'valor_total']

    def get_valor_total(self, obj):
        total = obj.atividade_set.aggregate(total=Sum('valor'))['total']
        return total or 0


class AtividadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atividade
        fields = '__all__'
        read_only_fields = ['id_usuario']

    def validate_data_cadastro(self, value):
        # RN12
        if value > date.today():
            raise serializers.ValidationError('A data de cadastro não pode ser no futuro.')
        return value


class EmpresaSerializer(serializers.ModelSerializer):
    setores_atendidos = serializers.SerializerMethodField()

    class Meta:
        model = Empresa
        fields = ['id', 'cnpj', 'razao_social', 'ramo_atividade', 'bairro', 'setores_atendidos']

    def get_setores_atendidos(self, obj):
        return sorted(set(obj.atendimentos.exclude(setor__nome__iexact='PROCON')
                          .values_list('setor__nome', flat=True)))

    def validate_cnpj(self, value):
        normalized = normalize_cnpj(value)
        try:
            validate_cnpj(normalized)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
        if Empresa.objects.filter(cnpj=normalized).exists():
            raise serializers.ValidationError('Esta empresa já está cadastrada.')
        return normalized


class AtendimentoSerializer(serializers.ModelSerializer):
    colaborador = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Atendimento
        fields = ['id', 'empresa', 'setor', 'colaborador', 'data_atendimento',
                  'desfecho', 'tipo', 'valor_credito', 'data_liberacao',
                  'vagas', 'data_abertura_vaga']
        extra_kwargs = {'setor': {'required': False}}

    def validate(self, attrs):
        user = self.context['request'].user
        if user.nivel_acesso != 'Administrador':
            if not user.id_setor_id:
                raise serializers.ValidationError('Seu usuário precisa estar vinculado a um setor.')
            attrs['setor'] = user.id_setor
        elif not (attrs.get('setor') or getattr(self.instance, 'setor_id', None)):
            raise serializers.ValidationError({'setor': 'Informe o setor.'})
        if self.instance:
            for field in ('empresa', 'setor'):
                old = getattr(self.instance, f'{field}_id')
                new = attrs.get(field)
                if new is not None and new.pk != old:
                    raise serializers.ValidationError({field: 'Este vínculo não pode ser alterado.'})
        return attrs
