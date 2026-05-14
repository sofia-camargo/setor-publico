from django.db import models

class Sector(models.Model):
    id_setor = models.AutoField(primary_key=True)
    nome_setor = models.CharField(max_length=255)
    sigla = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'setores'