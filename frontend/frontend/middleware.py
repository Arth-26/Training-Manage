import jwt
import requests
from datetime import datetime, timezone
from django.shortcuts import redirect
from .services.base_service import TOKEN_SERVICE  # seu serviço que chama a API
from django.conf import settings

class JWTAuthenticationMiddleware:
    """
    Middleware que garante que o request tenha um JWT válido.
    Atualiza o access_token se necessário e adiciona request.user_data
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        if access_token:
            try:
                # Decodifica sem validar assinatura
                decoded = jwt.decode(access_token, options={"verify_signature": False})
                exp_timestamp = decoded.get("exp")
                expiration = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
                if expiration < datetime.now(timezone.utc):
                    # Token expirado → tenta refresh
                    if refresh_token:
                        new_tokens = TOKEN_SERVICE.refresh_jwt_token(refresh_token)
                        if new_tokens:
                            access_token = new_tokens["access"]

                            request.COOKIES["access_token"] = access_token
                            # Atualiza o cookie na resposta
                            request._new_access_token = access_token
                        else:
                            return redirect("login")
                    else:
                        return redirect("login")
            except (jwt.ExpiredSignatureError, jwt.DecodeError):
                return redirect("login")

        # Processa a view
        response = self.get_response(request)

        # Atualiza o cookie se houve refresh
        if hasattr(request, "_new_access_token"):
            response.set_cookie(
                "access_token",
                request._new_access_token,
                httponly=True,
            )

        return response