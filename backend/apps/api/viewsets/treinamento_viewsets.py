from datetime import date
import os

from django.conf import settings
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (OpenApiExample, OpenApiResponse,
                                   extend_schema)
from rest_framework import parsers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.permissions import AlunoOnlyRead, IsInGroup
from apps.api.serializers.treinamento_serializer import (RecursosSerializer,
                                                         TreinamentoSerializer,
                                                         TurmaSerializer)
from apps.treinamento.models import Matricula, Recursos, Treinamento, Turma
from apps.users.models import Aluno


@extend_schema(tags=["Treinamentos"])
class TreinamentoViewSet(viewsets.ModelViewSet):
    ''' Gera operações CRUD para treinamentos'''
    serializer_class = TreinamentoSerializer
    permission_classes = [IsAuthenticated, IsInGroup, AlunoOnlyRead] 
    required_groups = ['admin', 'aluno']

    def get_queryset(self):
        ''' Retorna os treinamentos de acordo com o grupo do usuário.'''
        user = self.request.user
        if user.groups.filter(name='aluno').exists():
            return Treinamento.objects.filter(turmas__alunos=user.aluno).distinct()
        return Treinamento.objects.all().distinct()

@extend_schema(tags=["Turmas"])
class TurmaViewSet(viewsets.ModelViewSet):
    ''' Gera operações CRUD para turmas'''
    serializer_class = TurmaSerializer
    permission_classes = [IsAuthenticated, IsInGroup, AlunoOnlyRead] 
    required_groups = ['admin', 'aluno']

    def get_queryset(self):
        ''' Retorna as turmas de acordo com o grupo do usuário.'''
        user = self.request.user
        if user.groups.filter(name='aluno').exists():
            return Turma.objects.select_related('treinamento').filter(matriculas__aluno=user.aluno)
        return Turma.objects.select_related('treinamento').all()

@extend_schema(tags=["Recursos"])
class RecursosViewSet(viewsets.ModelViewSet):
    ''' Gera operações CRUD para recursos'''
    serializer_class = RecursosSerializer
    permission_classes = [IsAuthenticated, IsInGroup, AlunoOnlyRead] 
    required_groups = ['admin', 'aluno']
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_queryset(self):
        ''' Retorna os recursos de acordo com o grupo do usuário.'''
        qs = Recursos.objects.prefetch_related('turmas')

        user = self.request.user
        if user.groups.filter(name='aluno').exists():
            hoje = date.today()
            # Filtra recursos baseando-se em regras de acesso.
            # Drafts podem acessar os recursos mesmo que o treinamento tenha acabado
            # Acesso prévio pode acessar os recursos mesmo que o treinamento não tenha começado
            filtro = (
                Q(turmas__data_inicio__lte=hoje, turmas__data_fim__gte=hoje) |
                Q(draft=True, turmas__data_fim__lt=hoje) |
                Q(acesso_previo=True, turmas__data_inicio__gt=hoje)
            )
            qs = qs.filter(filtro, turmas__alunos=user.aluno)

        return qs.distinct()
    


class MatriculaAlunoTurma(APIView):
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = ['admin']

    def get_alunos(self, emails: list[str]) -> tuple[list[Aluno] | None, Response | None]:
        ''' Retorna os alunos correspondentes aos emails fornecidos.'''
        if not isinstance(emails, list) or not emails:
            return None, Response(
                {"erro": "Envie uma lista de emails no formato ['email1', 'email2', ...]."},
                status=status.HTTP_400_BAD_REQUEST
            )

        alunos = Aluno.objects.filter(user__email__in=emails)
        if not alunos.exists():
            return None, Response(
                {"erro": "Nenhum aluno encontrado com os emails informados."},
                status=status.HTTP_404_NOT_FOUND
            )
        return alunos, None

    @extend_schema(
        tags=["Turmas"],
        description="Adiciona um ou mais os alunos a uma turma.",
        request={
        "application/json": {
            "type": "object",
                "properties": {
                    "emails": {
                        "type": "array",
                        "items": {"type": "string", "format": "email"},
                        "example": ["email1@example.com", "email2@example.com"],
                        "description": "Lista de emails dos alunos a adicionar"
                    }
                },
                "required": ["alunos"]
            }
        },
        responses={
            200: OpenApiResponse(
                response=TurmaSerializer,
                description="Retorna a turma atualizada após adicionar os recursos."
            ),
        },
    )
    def post(self, request, turma_id: int) -> Response:
        ''' Adiciona alunos a uma turma. '''
        turma = get_object_or_404(Turma, id=turma_id)

        print(request.data)

        emails = request.data.get("emails", [])
        
        print(emails)
        alunos, error_response = self.get_alunos(emails)
        if error_response:
            return error_response
        
        Matricula.objects.bulk_create(
            [Matricula(
                aluno=aluno,
                turma=turma
            ) for aluno in alunos] 
        )

        serializer = TurmaSerializer(turma)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        tags=["Turmas"],
        description=(
            "Retira um ou todos os alunos de uma turma.\n\n"
            "**Casos de uso:**\n"
            "1. Enviar corpo com emails dos alunos → remove apenas esses alunos.\n"
            "2. Enviar `?delete_all=true` sem corpo → remove todos os alunos da turma."
        ),
    )
    def delete(self, request, turma_id: int) -> Response:
        ''' Retira alunos de uma turma. '''
        turma = get_object_or_404(Turma, id=turma_id)
        delete_all = request.query_params.get("delete_all", "false").lower() == "true"

        if delete_all:
            turma.matriculas.all().delete()
        else:
            emails = request.data.get("emails", [])
            alunos, error_response = self.get_alunos(emails)
            if error_response:
                return error_response
            
            turma.matriculas.filter(aluno__in=alunos).delete()

        serializer = TurmaSerializer(turma)
        return Response(serializer.data, status=status.HTTP_200_OK)



class RecursoDownloadView(APIView):
    permission_classes = [IsAuthenticated, IsInGroup, AlunoOnlyRead]
    required_groups = ['admin', 'aluno']

    @extend_schema(exclude=True)
    def get(self, request, turma_id):
        """
        Função para baixar o recurso da turma
        """
        try:
            turma = Turma.objects.get(pk=turma_id)
            
            caminho_relativo = turma.recurso.recurso.path
            print(caminho_relativo)
            caminho = os.path.join(caminho_relativo)
            print(caminho)
            if not os.path.exists(caminho):
                raise Http404("Arquivo não encontrado")

            filename = os.path.basename(caminho)
            return FileResponse(
                open(caminho, 'rb'),
                as_attachment=True,
                filename=filename,
            )
        except Exception as e:
            print(e)