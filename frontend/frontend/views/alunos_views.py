import sweetify
from django.shortcuts import redirect
from django.views.generic import TemplateView

from ..services.base_service import API_SERVICE
from .mixins import AdminGroupMixin, AuthenticatedUserMixin, DetailMixin, ListMixin, PostForm


class AlunoListView(AuthenticatedUserMixin, ListMixin, AdminGroupMixin, TemplateView):
    template_name = "alunos/aluno_list.html"

    def get_context_data(self, **kwargs):
        alunos_json = self.get_objects('alunos')
        self.update_pages_context(self.request, alunos_json)
        context = super().get_context_data(**kwargs)
        context['alunos'] = alunos_json.get('results')
        return context
    
class AlunoCreateView(AuthenticatedUserMixin, PostForm, AdminGroupMixin, TemplateView):
    template_name = "alunos/aluno_create.html"

    def post(self, request, *args, **kwargs):
        response = API_SERVICE.post_data(self.request, 'alunos/', request.POST)
        return self.valida_create(request, response, 'aluno_list', 'aluno')
        

class AlunoDetailView(AuthenticatedUserMixin, DetailMixin, AdminGroupMixin, TemplateView):
    template_name = "alunos/aluno_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = self.get_object('alunos')
        context['aluno'] = object
        context['turmas'] = object.get('turmas')
        return context
