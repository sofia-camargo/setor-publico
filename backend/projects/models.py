from django.db import models

class Project(models.Model):
    # O Django cria o ID automático, mas se no banco o nome for 'id_projeto', usamos primary_key=True
    id_projeto = models.AutoField(primary_key=True) 
    nome_projeto = models.CharField(max_length=255)
    data_inicio = models.DateField()
    data_prazo = models.DateField()
    status = models.CharField(max_length=50)
    
    # Relação com a tabela de usuários (o responsável)
    id_responsavel = models.ForeignKey('users.users', on_delete=models.CASCADE, db_column='id_responsavel')

    class Meta:
        managed = False      # IMPORTANTE: Diz ao Django para não tentar criar/alterar a tabela
        db_table = 'projetos' # Nome EXATO da tabela que está no DBeaver

    def __str__(self):
        return self.nome_projeto