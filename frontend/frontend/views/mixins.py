import math

from django.http import HttpResponseRedirect
from django.shortcuts import redirect
import sweetify

from ..services.base_service import API_SERVICE


class AuthenticatedUserMixin:
    """
    Mixin que busca o usuário autenticado via JWT e o injeta no context.
    """

    def get_data_user(self, request):
        """Obtém o usuário autenticado do backend usando o JWT armazenado em cookie."""
        user = API_SERVICE.get_data(request, "me/").json()
        self.user = user
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.get_data_user(self.request)
        return context
    

class AdminGroupMixin:

    def get_data_user(self, request):
        user = API_SERVICE.get_data(request, "me/").json()
        self.user = user
        return user

    def dispatch(self, request, *args, **kwargs):
        user = self.get_data_user(request)
        if self.user.get('grupo') != 'admin':
            sweetify.toast(
                request,
                'Você não tem permissão para acessar essa tela',
                icon='error',
                timer=3000,
                position='bottom-end',
            )
            return redirect(request.META.get('HTTP_REFERER'))
        return super().dispatch(request, *args, **kwargs)
    
class ListMixin:
    page = 1
    next_page = None
    previous_page = None
    qtd_pages = 1

    def get_objects(self, obj):
        """Requisita uma lista de objetos."""
        page = self.request.GET.get('page') or 1
        json = API_SERVICE.get_data(self.request, f"{obj}/", page).json()
        return json

    def update_pages_context(self, request, lista_obj):
        self.page = int(request.GET.get('page', 1))
        if lista_obj.get('next'):
            self.next_page = self.page + 1
        if lista_obj.get('previous'):
            self.previous_page = self.page - 1
        
        self.qtd_pages = math.ceil(int(lista_obj.get('count')) / 10)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page"] = self.page
        context["next_page"] = self.next_page
        context["previous_page"] = self.previous_page
        context["qtd_pages"] = self.qtd_pages
        context["qtd_pages_list"] = range(1, self.qtd_pages + 1)
        return context

class PostForm:
    def valida_create(self, request, response, url_redirect, obj):
        if response.status_code in (200, 201):
            sweetify.toast(
                request,
                f'{obj.title()} cadastrado com sucesso',
                icon='success',
                timer=3000,
                position='bottom-end',
            )
            return redirect(url_redirect)
        elif response.status_code == 400:
            erros = [valor[0] for valor in response.json().values()]
            mensagem_erro = "<br><br>".join(erros)
            sweetify.toast(
                request,
                mensagem_erro,
                icon='error',
                timer=3000,
                position='bottom-end',
            )
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            return redirect(request.META.get('HTTP_REFERER'))
        
class DetailMixin:
    def get_object(self, obj):
        id_object = self.kwargs['id']
        object = API_SERVICE.get_data(self.request, f'{obj}/{id_object}').json()
        return object