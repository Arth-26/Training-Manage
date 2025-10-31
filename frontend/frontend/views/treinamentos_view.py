from django.views.generic import TemplateView

from ..services.base_service import API_SERVICE
from .mixins import AdminGroupMixin, AuthenticatedUserMixin, DetailMixin, ListMixin, PostForm


class TreinamentoListView(AuthenticatedUserMixin, ListMixin, AdminGroupMixin, TemplateView):
    template_name = "treinamentos/treinamento_list.html"

    def get_context_data(self, **kwargs):
        treinamentos_json = self.get_objects('treinamentos')
        self.update_pages_context(self.request, treinamentos_json)
        context = super().get_context_data(**kwargs)
        context['treinamentos'] = treinamentos_json.get('results')
        return context
    
class TreinamentoCreateView(AuthenticatedUserMixin, PostForm, AdminGroupMixin, TemplateView):
    template_name = "treinamentos/treinamento_create.html"

    def post(self, request, *args, **kwargs):
        response = API_SERVICE.post_data(self.request, 'treinamentos/', request.POST)
        return self.valida_create(request, response, 'treinamento_list', 'treinamento')
    
class TreinamentoDetailView(AuthenticatedUserMixin, DetailMixin, AdminGroupMixin, TemplateView):
    template_name = "treinamentos/treinamento_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = self.get_object('treinamentos')
        context['treinamento'] = object
        context['turmas'] = object.get('turmas')
        return context