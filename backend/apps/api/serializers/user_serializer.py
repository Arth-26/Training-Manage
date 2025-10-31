from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from rest_framework import serializers

from apps.users.models import Aluno

User = get_user_model()


class AdminSerializer(serializers.ModelSerializer):
    grupo = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'grupo']

    def get_grupo(self, obj) -> str:
        if obj.is_superuser:
            return 'admin'
        return obj.groups.all().first().name

    def create(self, validated_data):
        ''' Cria um usuário administrador. '''
        user = User.objects.create_user(
            **validated_data
        )
        group, created = Group.objects.get_or_create(name='admin')
        user.groups.add(group)
        return user
    
class AdminUpdateSerializer(serializers.ModelSerializer):
    senha_antiga = serializers.CharField(write_only=True)
    senha_nova = serializers.CharField(write_only=True)
    senha_confirmacao = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'senha_antiga', 'senha_nova', 'senha_confirmacao']

    def validate(self, attrs):
        ''' Valida os campos de senha para atualização. '''
        senha_antiga = attrs.get('senha_antiga')
        senha_nova = attrs.get('senha_nova')
        senha_confirmacao = attrs.get('senha_confirmacao')

        if any([senha_antiga, senha_nova, senha_confirmacao]):
            if not all([senha_antiga, senha_nova, senha_confirmacao]):
                raise serializers.ValidationError("Todos os campos de senha devem ser preenchidos para alterar a senha.")
            if senha_nova != senha_confirmacao:
                raise serializers.ValidationError("A nova senha e a confirmação não coincidem.")

        return attrs
    
    def update(self, instance, validated_data):
        ''' Atualiza os dados do administrador, incluindo a senha se fornecida. '''
        senha_antiga = validated_data.pop('senha_antiga', None)
        nova_senha = validated_data.pop('senha_nova', None)
        senha_confirmacao = validated_data.pop('senha_confirmacao', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if senha_antiga and nova_senha and senha_confirmacao:
            if not instance.check_password(senha_antiga):
                raise serializers.ValidationError({"senha_antiga": "Senha antiga incorreta."})
            instance.set_password(nova_senha)

        instance.save()
        
        return instance


class AlunoSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='user.id', read_only=True)
    nome = serializers.CharField(source='user.username')
    sobrenome = serializers.CharField(source='user.last_name', required=True)
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True)
    turmas = serializers.SerializerMethodField()
    grupo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Aluno
        fields = ['id', 'nome', 'sobrenome', 'email', 'telefone', 'password', 'turmas', 'grupo']

    def get_grupo(self, obj) -> str:
        return obj.user.groups.all().first().name

    def get_turmas(self, obj) -> list[dict]:
        return [
            {
                'id': matricula.turma.id,
                'treinamento': matricula.turma.treinamento.nome,
                'nome': matricula.turma.nome,
                'inicio': matricula.turma.data_inicio,
                'fim': matricula.turma.data_fim
            }
            for matricula in obj.matriculas.select_related('turma', 'turma__treinamento').all()
        ]
    
    def validate_nome(self, value):
        if not value.isalpha():
            raise serializers.ValidationError('O nome deve conter apenas caracteres alfabeticos')
        return value
    
    def validate_sobrenome(self, value):
        if not value.isalpha():
            raise serializers.ValidationError('O sobrenome deve conter apenas caracteres alfabeticos')
        return value
    
    def validate_telefone(self, value):
        if not value.isdigit() or len(value) != 13:
            raise serializers.ValidationError('O número de telefone deve conter 13 dígitos no formato: "55DDD912345678" (sem parênteses ou outros caracteres)')

        return f'+{value}'
    
    def create(self, validated_data):
        ''' Cria um usuário aluno e associa ao grupo "aluno". '''
        user_data = validated_data.pop('user')
        user = User.objects.create_user(
            **user_data
        )
        aluno = Aluno.objects.create(user=user, telefone = validated_data.get('telefone'))
        group, created = Group.objects.get_or_create(name='aluno')
        user.groups.add(group)
        return aluno

        
class AlunoUpdateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='user.id', read_only=True)
    nome = serializers.CharField(source='user.username')
    sobrenome = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    senha_antiga = serializers.CharField(write_only=True)
    senha_nova = serializers.CharField(write_only=True)
    senha_confirmacao = serializers.CharField(write_only=True)
    

    class Meta:
        model = Aluno
        fields = ['id', 'nome', 'sobrenome', 'email', 'telefone', 'senha_antiga', 'senha_nova', 'senha_confirmacao']

    def validate(self, attrs):
        ''' Valida os campos de senha para atualização. '''
        senha_antiga = attrs.get('senha_antiga')
        senha_nova = attrs.get('senha_nova')
        senha_confirmacao = attrs.get('senha_confirmacao')

        if any([senha_antiga, senha_nova, senha_confirmacao]):
            if not all([senha_antiga, senha_nova, senha_confirmacao]):
                raise serializers.ValidationError("Todos os campos de senha devem ser preenchidos para alterar a senha.")
            if senha_nova != senha_confirmacao:
                raise serializers.ValidationError("A nova senha e a confirmação não coincidem.")

        return attrs
    
    def update(self, instance, validated_data):
        ''' Atualiza os dados do aluno, incluindo a senha se fornecida. '''
        user_data = validated_data.pop('user', {})
        senha_antiga = validated_data.pop('senha_antiga', None)
        nova_senha = validated_data.pop('senha_nova', None)
        senha_confirmacao = validated_data.pop('senha_confirmacao', None)

        user = instance.user

        for attr, value in user_data.items():
            setattr(user, attr, value)

        if senha_antiga and nova_senha and senha_confirmacao:
            if not user.check_password(senha_antiga):
                raise serializers.ValidationError({"senha_antiga": "Senha antiga incorreta."})
            user.set_password(nova_senha)

        user.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance