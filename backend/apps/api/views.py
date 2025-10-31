from django.shortcuts import render

# Create your views here.
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


#Esconde as views de obtenção de tokens do jwt da documentação Swagger
@extend_schema(exclude=True)
class HiddenTokenObtainPairView(TokenObtainPairView):
    pass

@extend_schema(exclude=True)
class HiddenTokenRefreshView(TokenRefreshView):
    pass