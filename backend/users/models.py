from django.db import models
# 1. Aqui: Importando com S maiúsculo!
from sector.models import Sector 

class Users(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    funcao = models.CharField(max_length=255, null=True, blank=True)
    matricula = models.IntegerField(null=True, blank=True)

    id_setor = models.ForeignKey(
        'sector.Sector', 
        on_delete=models.CASCADE, 
        db_column='id_setor'  
    )
    

    class Meta:
        managed = False
        db_table = 'usuarios'