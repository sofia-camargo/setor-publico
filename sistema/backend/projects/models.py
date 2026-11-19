from django.db import models

class Project(models.Model):
    id_projeto = models.AutoField(primary_key=True) 
    nome = models.CharField(max_length=255)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    prioridade = models.CharField(max_length=50, null=True, blank=True)
    status_tag = models.CharField(max_length=100)
    
    id_responsavel = models.ForeignKey('users.Users', on_delete=models.CASCADE, db_column='id_responsavel', null=True, blank=True)
    id_setor = models.ForeignKey('sector.Sector', on_delete=models.CASCADE, db_column='id_setor', null=True, blank=True)

    class Meta:
        db_table = 'projetos'

    def __str__(self):
        return self.nome

class Tarefa(models.Model):
    id_tarefa = models.AutoField(primary_key=True)
    id_projeto = models.ForeignKey(Project, on_delete=models.CASCADE, db_column='id_projeto')
    nome_tarefa = models.CharField(max_length=255)
    responsavel_nome = models.CharField(max_length=255)
    data_inicio = models.DateField()
    data_final = models.DateField()
    concluida = models.BooleanField(default=False)
    data_conclusao = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'tarefas'