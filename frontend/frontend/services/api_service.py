import requests
from django.shortcuts import redirect
from dotenv import load_dotenv
import os

load_dotenv()

from frontend.services.token_service import TokenService

class APIService:
    
    token_service = TokenService()
    BASE_URL = str(os.getenv("API_URL", "http://localhost:8000/api/"))  

    def get_headers(self, request):
        """
        Retorna os headers com Authorization usando o access_token já garantido pelo middleware.
        """
        access_token = request.COOKIES.get("access_token")
        if not access_token:
            return redirect("login")
        return {"Authorization": f"Bearer {access_token}"}

    def get_data(self, request, endpoint, page=None, stream=False):
        headers = self.get_headers(request)
        if page:
            endpoint = f'{endpoint}?page={page}'
        response = requests.get(f"{self.BASE_URL}/{endpoint}", headers=headers, stream=stream)

        
        if response.status_code in (200, 201):
            return response
        else:
            try:
                print("Erro do backend:", response.json())
            except Exception:
                print("Erro do backend:", response.text)
            response.raise_for_status()

    def post_data(self, request, endpoint, data):
        headers = self.get_headers(request)
        response = requests.post(f"{self.BASE_URL}/{endpoint}", json=data, headers=headers)
        return response

    def post_media_data(self, request, endpoint, data, file):
        headers = self.get_headers(request)
        files = {"recurso": (file.name, file.read(), file.content_type)}
        response = requests.post(f"{self.BASE_URL}/{endpoint}", data=data, files=files, headers=headers)
        if response.status_code in (200, 201):
            return response
        else:
            try:
                print("Erro do backend:", response.json())
            except Exception:
                print("Erro do backend:", response.text)
            response.raise_for_status()