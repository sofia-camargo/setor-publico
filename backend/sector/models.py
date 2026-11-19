from django.db import models

class Sector(models.Model):
    id_setor = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)

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