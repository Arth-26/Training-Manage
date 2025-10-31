from django.conf.urls.static import static
from django.urls import path
from django.conf import settings


from .views.base_views import HomeView, LoginView
from .views.alunos_views import AlunoCreateView, AlunoDetailView, AlunoListView
from .views.treinamentos_view import TreinamentoDetailView, TreinamentoListView, TreinamentoCreateView
from .views.turmas_views import RecursoCreateView, TurmaCreateView, TurmaDetailView, TurmaListView, ViewMatricularAluno, baixar_recurso


urlpatterns = [
   path('', LoginView.as_view(), name="login"),
   path('home/', HomeView.as_view(), name="home"),

   # Alunos
   path('alunos/lista', AlunoListView.as_view(), name='aluno_list'),
   path('alunos/cadastro', AlunoCreateView.as_view(), name='aluno_create'),
   path('alunos/<uuid:id>', AlunoDetailView.as_view(), name='aluno_detail'),
   path('alunos/matricular/turma/<int:id>', ViewMatricularAluno.as_view(), name='aluno_matricular'),

   #Treinamentos
   path('treinamentos/lista', TreinamentoListView.as_view(), name='treinamento_list'),
   path('treinamentos/cadastro', TreinamentoCreateView.as_view(), name='treinamento_create'),
   path('treinamentos/<int:id>', TreinamentoDetailView.as_view(), name='treinamento_detail'),

   #Turmas
   path('turmas/lista', TurmaListView.as_view(), name='turma_list'),
   path('turmas/cadastro', TurmaCreateView.as_view(), name='turma_create'),
   path('turmas/<int:id>', TurmaDetailView.as_view(), name='turma_detail'),
   path('turmas/<int:id>/cadastro-recurso', RecursoCreateView.as_view(), name='recurso_create'),
   path('turmas/<int:id>/baixar_recurso', baixar_recurso, name='baixar_recurso'),
   
] + static(settings.STATIC_ROOT, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)