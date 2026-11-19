from django.db import models
from sector.models import Sector 

class Users(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    matricula = models.CharField(max_length=100, unique=True)
    nome = models.CharField(max_length=255)
    senha_hash = models.CharField(max_length=255)
    funcao = models.CharField(max_length=255, null=True, blank=True)
    nivel_acesso = models.CharField(max_length=50)
    id_setor = models.ForeignKey(
        'sector.Sector', 
        on_delete=models.CASCADE, 
        db_column='id_setor',
        null=True, blank=True
    )

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return self.nome

    @property
    def is_authenticated(self):
        return True

class HistoricoSenhas(models.Model):
    id_historico = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='resets_recebidos', db_column='id_usuario')
    id_responsavel = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='resets_realizados', db_column='id_responsavel')
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'historico_senhas'
