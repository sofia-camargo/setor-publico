from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

from .cnpj import validate_cnpj

class Sector(models.Model):
    id_setor = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=10, unique=True, null=True, blank=True,
                              choices=[('SEBRAE', 'SEBRAE Aqui'), ('BP', 'Banco do Povo'),
                                       ('PAT', 'PAT'), ('PROCON', 'PROCON')])

    class Meta:
        db_table = 'setores'

    def __str__(self):
        return self.nome

class Indicador(models.Model):
    id_indicador = models.AutoField(primary_key=True)
    id_setor = models.ForeignKey(Sector, on_delete=models.CASCADE, db_column='id_setor', null=True, blank=True)
    nome = models.CharField(max_length=255)
    tipo_dado = models.CharField(max_length=50)

    class Meta:
        db_table = 'indicadores'

class Atividade(models.Model):
    id_atividade = models.AutoField(primary_key=True)
    id_indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, db_column='id_indicador', null=True, blank=True)
    id_usuario = models.ForeignKey('users.Users', on_delete=models.CASCADE, db_column='id_usuario', null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_cadastro = models.DateField()

    class Meta:
        db_table = 'atividades'

class Empresa(models.Model):
    cnpj = models.CharField(max_length=14, unique=True, validators=[validate_cnpj])
    razao_social = models.CharField(max_length=255)
    ramo_atividade = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)

    class Meta:
        db_table = 'empresas'

    def save(self, *args, **kwargs):
        self.cnpj = validate_cnpj(self.cnpj)
        self.full_clean()
        super().save(*args, **kwargs)


class Atendimento(models.Model):
    SEBRAE = 'SEBRAE_ORIENTACAO'
    CREDITO = 'BP_LIBERACAO'
    VAGA = 'PAT_VAGA'
    OUTRO = 'OUTRO'
    TIPOS = [(SEBRAE, 'Orientação SEBRAE'), (CREDITO, 'Crédito liberado'),
             (VAGA, 'Vaga captada'), (OUTRO, 'Outro atendimento')]

    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name='atendimentos')
    setor = models.ForeignKey(Sector, on_delete=models.PROTECT)
    colaborador = models.ForeignKey('users.Users', on_delete=models.PROTECT)
    data_atendimento = models.DateField()
    desfecho = models.CharField(max_length=100)
    tipo = models.CharField(max_length=25, choices=TIPOS)
    valor_credito = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    data_liberacao = models.DateField(null=True, blank=True)
    vagas = models.PositiveIntegerField(null=True, blank=True)
    data_abertura_vaga = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'atendimentos'
        ordering = ['data_atendimento', 'pk']

    def clean(self):
        errors = {}
        if self.data_atendimento and self.data_atendimento > date.today():
            errors['data_atendimento'] = 'A data não pode estar no futuro.'
        sector_code = self.setor.codigo if self.setor_id else None
        expected = {self.SEBRAE: 'SEBRAE', self.CREDITO: 'BP', self.VAGA: 'PAT'}
        if self.tipo in expected and sector_code != expected[self.tipo]:
            errors['tipo'] = 'O tipo não corresponde ao setor do atendimento.'
        if self.tipo == self.CREDITO:
            if self.valor_credito is None or self.valor_credito <= 0:
                errors['valor_credito'] = 'Informe o valor positivo do crédito liberado.'
            if not self.data_liberacao:
                errors['data_liberacao'] = 'Informe a data da liberação.'
            elif self.data_atendimento and self.data_liberacao < self.data_atendimento:
                errors['data_liberacao'] = 'A liberação deve ocorrer após o atendimento.'
            elif self.data_liberacao > date.today():
                errors['data_liberacao'] = 'A liberação não pode estar no futuro.'
        elif self.valor_credito is not None or self.data_liberacao is not None:
            errors['tipo'] = 'Dados de crédito exigem o tipo BP_LIBERACAO.'
        if self.tipo == self.VAGA:
            if not self.vagas or self.vagas < 1:
                errors['vagas'] = 'Informe ao menos uma vaga.'
            if not self.data_abertura_vaga:
                errors['data_abertura_vaga'] = 'Informe a data de abertura da vaga.'
            elif self.data_atendimento and self.data_abertura_vaga < self.data_atendimento:
                errors['data_abertura_vaga'] = 'A abertura deve ocorrer após o atendimento.'
            elif self.data_abertura_vaga > date.today():
                errors['data_abertura_vaga'] = 'A abertura não pode estar no futuro.'
        elif self.vagas is not None or self.data_abertura_vaga is not None:
            errors['tipo'] = 'Dados de vagas exigem o tipo PAT_VAGA.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.pk:
            original = Atendimento.objects.get(pk=self.pk)
            if (original.setor_id, original.colaborador_id, original.empresa_id) != (self.setor_id, self.colaborador_id, self.empresa_id):
                raise ValidationError('Empresa, setor e colaborador não podem ser alterados.')
        self.full_clean()
        super().save(*args, **kwargs)
