
import os
import re
from datetime import date, timedelta

from django.conf import settings
from rest_framework import serializers

from apps.treinamento.models import Recursos, Treinamento, Turma


class TreinamentoSerializer(serializers.ModelSerializer):
    turmas = serializers.SerializerMethodField()
    class Meta:
        model = Treinamento
        fields = ['id', 'nome', 'descricao', 'turmas']

    def get_turmas(self, obj) -> list[dict]:
        return [
            {
                'nome': turma.nome,
                'inicio': turma.data_inicio,
                'fim': turma.data_fim,
                'link_acesso': turma.link_acesso
            }
            for turma in obj.turmas.all()
        ]
    
    def validate_nome(self, value):
        if value.isdigit():
            raise serializers.ValidationError('O nome do treinamento não pode ter apenas números')
        return value

class TurmaSerializer(serializers.ModelSerializer):
    alunos = serializers.SerializerMethodField()
    recurso = serializers.SerializerMethodField()
    treinamento_nome = serializers.CharField(source='treinamento.nome', read_only=True)
    treinamento = serializers.PrimaryKeyRelatedField(queryset=Treinamento.objects.all(), write_only=True)
    class Meta:
        model = Turma
        fields = ['treinamento', 'treinamento_nome', 'id', 'nome', 'data_inicio', 'data_fim', 'link_acesso', 'alunos', 'recurso']
    
    def validate_nome(self, value):
        if value.isdigit():
            raise serializers.ValidationError('O nome da turma não pode ter apenas números')
        return value
    

    def get_alunos(self, obj) -> list[dict]:
        return [
            {
                'nome': f'{matricula.aluno.user.username} {matricula.aluno.user.last_name}' ,
                'email': matricula.aluno.user.email,
                'telefone': matricula.aluno.telefone,
            }
            for matricula in obj.matriculas.select_related('aluno', 'aluno__user').all()
        ]

    def get_recurso(self, obj) -> dict[str, str]:
        user = self.context['request'].user
        hoje = date.today()

        try:
            recurso = obj.recurso
        except Turma.recurso.RelatedObjectDoesNotExist:
            return {}

        if user.groups.filter(name='aluno').exists():
            print('Entrou')
            print(obj.data_inicio)
            print(obj.data_fim)
            
            if hoje < obj.data_inicio and not recurso.acesso_previo:
                return {'bloqueia_acesso': True}
            
            if hoje > obj.data_fim and not recurso.draft:
                return {'bloqueia_acesso': True}

        return {
            "nome": recurso.nome_recurso,
            "tipo": recurso.tipo_recurso,
            "link": recurso.recurso.url
        }

    def validate(self, data):
        ''' Valida datas de inicio e fim da turma. '''
        if data['data_fim'] < data['data_inicio']:
            raise serializers.ValidationError("A data de fim não pode ser anterior à data de início.")
        
        hoje = date.today()
        if data['data_fim'] > hoje + timedelta(days=5*365):
            raise serializers.ValidationError("A data de fim não pode ser mais que 5 anos a frente da data atual.")
        
        if data['data_inicio'] < hoje:
            raise serializers.ValidationError("A data de inicio deve ser maior ou igual a data de hoje.")
        
        return data

class RecursosSerializer(serializers.ModelSerializer):
    turma_nome = serializers.CharField(source='turma.nome', read_only=True)
    turma = serializers.PrimaryKeyRelatedField(queryset=Turma.objects.all(), write_only=True)
    class Meta:
        model = Recursos
        fields = ['id', 'turma', 'turma_nome', 'tipo_recurso', 'recurso', 'acesso_previo', 'draft', 'nome_recurso', 'descricao_recurso']

    def validate(self, data):
        ''' Valida o tipo e o nome do arquivo do recurso. '''
        recurso = data.get('recurso') 
        arquivo_name = recurso.name.replace(" ", "_")  
        regex_caracteres_invalidos = re.compile(r"[^A-Za-z0-9._\-]")
        regex_acentos = re.compile(r"[\u00C0-\u017F]")

        if data['tipo_recurso'] == 'video' and not recurso.name.endswith(('.mp4', '.avi', '.mov')):
            raise serializers.ValidationError("O recurso deve ser um arquivo de vídeo válido.")
        elif data['tipo_recurso'] == 'pdf' and not recurso.name.endswith('.pdf'):
            raise serializers.ValidationError("O recurso deve ser um arquivo PDF válido.")
        elif data['tipo_recurso'] == 'zip' and not recurso.name.endswith('.zip'):
            raise serializers.ValidationError("O recurso deve ser um arquivo ZIP válido.")
        
        if regex_caracteres_invalidos.search(arquivo_name) or regex_acentos.search(arquivo_name):
            raise serializers.ValidationError("O nome do arquivo contém caracteres inválidos. Use apenas letras, números, pontos, hífens e sublinhados, sem acentos.")

        return data

    def create(self, validated_data):
        ''' Cria um recurso, evitando duplicação de arquivos. '''
        arquivo = validated_data.get('recurso')
        
        arquivo_name = arquivo.name.replace(" ", "_")
        caminho_arquivo = os.path.join(settings.MEDIA_ROOT, 'recursos', arquivo_name)


        if os.path.exists(caminho_arquivo):
            validated_data['recurso'] = f"recursos/{arquivo_name}"
            return Recursos.objects.create(**validated_data)

        return super().create(validated_data)