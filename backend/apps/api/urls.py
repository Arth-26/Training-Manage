from django.conf.urls.static import static
from django.urls import path

from .viewsets.treinamento_viewsets import (MatriculaAlunoTurma, RecursoDownloadView)
from .viewsets.user_viewsets import AlunoWithoutPages, MeView

urlpatterns = [
    path('me/', MeView.as_view(), name='me'),

    path('turmas/<int:turma_id>/alunos/', MatriculaAlunoTurma.as_view(), name='alunos_turma'),
    path('turmas/<int:turma_id>/baixar_recurso/', RecursoDownloadView.as_view(), name='baixa_recurso'),

    path('alunos/todos', AlunoWithoutPages.as_view(), name='todos_alunos')
]


