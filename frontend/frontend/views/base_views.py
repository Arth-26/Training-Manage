from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import TemplateView
import sweetify

from ..services.base_service import API_SERVICE, TOKEN_SERVICE
from .mixins import AuthenticatedUserMixin, ListMixin


class LoginView(TemplateView):
    template_name = "login.html"

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        password = request.POST.get("password")

        tokens = TOKEN_SERVICE.get_tokens(email, password)

        if tokens == '401':
            sweetify.toast(
                request,
                'Email ou senha inválidos. Tente novamente.',
                icon='error',
                timer=3000,
                position='bottom-end',
            )
            return redirect(request.META.get('HTTP_REFERER'))
        
        response = redirect('home')
        response.set_cookie("access_token", tokens["access"], httponly=True)
        response.set_cookie("refresh_token", tokens["refresh"], httponly=True)   

        return response
    
class HomeView(AuthenticatedUserMixin, ListMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.user.get('grupo') == 'aluno':
            context['turmas'] = self.user.get('turmas')
        return context 