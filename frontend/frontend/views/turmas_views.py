from django.http import FileResponse, HttpResponseRedirect
from django.views.generic import TemplateView

from ..services.base_service import API_SERVICE
from .mixins import AdminGroupMixin, AuthenticatedUserMixin, DetailMixin, ListMixin, PostForm


class TurmaListView(AuthenticatedUserMixin, ListMixin, AdminGroupMixin, TemplateView):
    template_name = "turmas/turma_list.html"

    def get_context_data(self, **kwargs):
        turmas_json = self.get_objects('turmas')
        self.update_pages_context(self.request, turmas_json)
        context = super().get_context_data(**kwargs)
        context['turmas'] = turmas_json.get('results')
        return context
    
class TurmaCreateView(AuthenticatedUserMixin, PostForm, AdminGroupMixin, TemplateView):
    template_name = "turmas/turma_create.html"

    def post(self, request, *args, **kwargs):
        response = API_SERVICE.post_data(self.request, 'turmas/', request.POST)
        return self.valida_create(request, response, 'turma_list', 'turma')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['treinamentos'] = API_SERVICE.get_data(self.request, 'treinamentos/').json().get('results')
        return context
    

class TurmaDetailView(AuthenticatedUserMixin, DetailMixin, TemplateView):
    template_name = "turmas/turma_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = self.get_object('turmas')
        print(object)
        context['turma'] = object
        context['alunos'] = object.get('alunos')
        return context
    
class RecursoCreateView(AuthenticatedUserMixin, PostForm, DetailMixin, AdminGroupMixin, TemplateView):
    template_name = "turmas/cadastrar_recurso.html"

    def post(self, request, *args, **kwargs):
        arquivo = request.FILES['recurso']
        response = API_SERVICE.post_media_data(self.request, 'recursos/', request.POST, arquivo)
        return self.valida_create(request, response, 'turma_list', 'turma')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = self.get_object('turmas')
        context['turma'] = object
        return context
    
class ViewMatricularAluno(AuthenticatedUserMixin, PostForm, DetailMixin, AdminGroupMixin, TemplateView):
    template_name = "alunos/matricular_alunos.html"

    def post(self, request, *args, **kwargs):
        turma_id = self.kwargs['id']
        data = {
            'emails':request.POST.getlist('emails')
        }
        response = API_SERVICE.post_data(self.request, f'turmas/{turma_id}/alunos/', data)
        return self.valida_create(request, response, 'turma_list', 'alunos')
    
    def get_alunos(self):
        response = API_SERVICE.get_data(self.request, 'alunos/todos').json()
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = self.get_object('turmas')
        context['alunos'] = self.get_alunos()
        context['turma'] = object
        return context
    

def baixar_recurso(request, id):
    """
    Faz download do recurso no computador local.
    """

    endpoint = f"turmas/{id}/baixar_recurso/"
    response = API_SERVICE.get_data(request, endpoint, stream=True)

    if response.status_code != 200:
        # Erro inesperado → volta pra tela anterior
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    # Extrai o nome do arquivo do header HTTP
    filename = response.headers.get("Content-Disposition").split("filename=")[-1].strip('"')

    return FileResponse(response.raw, as_attachment=True, filename=filename)
