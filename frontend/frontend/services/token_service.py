import requests
from dotenv import load_dotenv
import os

load_dotenv()

class TokenService:

    BASE_URL = str(os.getenv("API_URL", "http://localhost:8000/api/"))

    def get_tokens(self, email: str, password: str) -> dict:
        response = requests.post(f"{self.BASE_URL}/token/", data={"email": email, "password": password})
        if response.status_code == 401:
            return '401'
        if response.status_code == 200:
            tokens = response.json()
            return tokens
        else:
            response.raise_for_status()

    def refresh_jwt_token(self, refresh_token) -> dict:
        response = requests.post(f"{self.BASE_URL}/token/refresh/", data={"refresh": refresh_token})
        if response.status_code == 200:
            return response.json()
        return None