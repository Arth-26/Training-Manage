from rest_framework import routers

from apps.api.viewsets.treinamento_viewsets import (RecursosViewSet,
                                                    TreinamentoViewSet,
                                                    TurmaViewSet)
from apps.api.viewsets.user_viewsets import AdminViewSet, AlunoViewSet

route = routers.DefaultRouter()


#Registra as rotas das viewsets da API
route.register(r'admin', AdminViewSet, basename='admin')
route.register(r'alunos', AlunoViewSet, basename='alunos')
route.register(r'treinamentos', TreinamentoViewSet, basename='treinamentos')
route.register(r'turmas', TurmaViewSet, basename='turmas')
route.register(r'recursos', RecursosViewSet, basename='recursos')