
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample

from apps.api.permissions import IsInGroup, OnlySuperUser
from apps.api.serializers.user_serializer import (AdminSerializer, AdminUpdateSerializer, AlunoSerializer,
                                                  AlunoUpdateSerializer, User)
from apps.users.models import Aluno

@extend_schema(tags=["Administradores"])
class AdminViewSet(viewsets.ModelViewSet):
    '''Gera as operações CRUD para usuários administradores'''
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, OnlySuperUser] 

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return AdminUpdateSerializer
        return AdminSerializer
    
@extend_schema(tags=["Alunos"])
class AlunoViewSet(viewsets.ModelViewSet):
    '''Gera as operações CRUD para usuários alunos'''
    queryset = Aluno.objects.select_related('user').all()
    permission_classes = [IsAuthenticated, IsInGroup] 
    required_groups = ['admin']

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return AlunoUpdateSerializer
        return AlunoSerializer

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        '''Remove um aluno e o usuário associado.'''
        instance = self.get_object()
        user = instance.user

        user.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AlunoWithoutPages(APIView):
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = ['admin']
    pagination_class = None

    def get(self, request):
        alunos = Aluno.objects.all()
        serializer = AlunoSerializer(alunos, many=True)
        return Response(serializer.data)


@extend_schema(exclude=True)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.groups.filter(name='aluno').exists():
            serializer = AlunoSerializer(request.user.aluno)
        else:
            serializer = AdminSerializer(request.user)
        return Response(serializer.data)
