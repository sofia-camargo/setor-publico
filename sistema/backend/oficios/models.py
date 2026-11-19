from django.db import models
from users.models import Users
from sector.models import Sector

class Oficios(models.Model):
    id_oficio = models.AutoField(primary_key=True)
    numero_sequencial = models.IntegerField()
    ano = models.IntegerField()
    assunto = models.CharField(max_length=255)
    data_oficio = models.DateField()
    id_usuario = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='id_usuario', null=True, blank=True)
    id_setor = models.ForeignKey(Sector, on_delete=models.CASCADE, db_column='id_setor', null=True, blank=True)

    class Meta:
        db_table = 'oficios'
        constraints = [
            models.UniqueConstraint(
                fields=['ano', 'numero_sequencial'],
                name='oficio_numero_unico_por_ano'
            )
        ]
