from django.db import models
from django.forms import ValidationError

from apps.users.models import Aluno

class Treinamento(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    descricao = models.CharField(max_length=255)

    def __str__(self):
        return self.nome

class Turma(models.Model):
    treinamento = models.ForeignKey(Treinamento, on_delete=models.CASCADE, related_name='turmas')
    nome = models.CharField(max_length=255)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    link_acesso = models.URLField()
    

    def __str__(self):
        return (self.nome + " - " + self.treinamento.nome)
    
    class Meta:
        unique_together = ('treinamento', 'nome')

class Recursos(models.Model):
    turma = models.OneToOneField(Turma, null=True, blank=True, on_delete=models.SET_NULL, related_name='recurso')
    tipo_recurso = models.CharField(max_length=50, choices=[('video', 'Video'), ('pdf', 'PDF'), ('zip', 'ZIP')])
    recurso = models.FileField(upload_to='recursos/')
    acesso_previo = models.BooleanField(default=False)
    draft = models.BooleanField(default=True)
    nome_recurso = models.CharField(max_length=255)
    descricao_recurso = models.CharField(max_length=255)

    def __str__(self):
        return (self.nome_recurso + " - " + self.tipo_recurso)
    
    class Meta:
        unique_together = ('tipo_recurso', 'nome_recurso')

class Matricula(models.Model):
    aluno = models.ForeignKey('users.Aluno', on_delete=models.CASCADE, related_name='matriculas')
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='matriculas')

    class Meta:
        unique_together = ('aluno', 'turma')

    def __str__(self):
        return f"{self.aluno.user.nome} - {self.turma.nome}"

