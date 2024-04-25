from functools import lru_cache
from typing import Optional
from datetime import datetime, timedelta
import json
import requests
from sql_app.core.config import settings

class VitteApiClientBase():
    accept_str = 'application/json, text/plain, */*'
    encoding_str = 'gzip, deflate, br'

    def __init__(self, empresa_id=None, client_id=None):
        self.session = requests.Session()
        self.base_url = "https://app.vitte.com.ar/api"
        self.empresa_id = empresa_id
        self.client_id = client_id
        self.token = None
        self.token_expiry = datetime.now()

        # Initialize from environment variables or configuration
        self.login_dict = {
            'clave': settings.VITTE_CLAVE,
            'server': settings.VITTE_SERVER,
            'usuario': settings.VITTE_USUARIO,
            'validate': "",
        }

    def _fetch_token_and_usuario_id(self):
        if self.token is None or datetime.now() >= self.token_expiry:
            print('VITTE_CLIENT: Refreshing token...')
            login_url = f'{self.base_url}/seguridad/login'
            response = self.session.post(url=login_url, json=self.login_dict).json()
            print(f'respuesta de login_url: {response}')
            if 'result' in response and 'token' in response['result']:
                print('encontro algo')
                self.token = response['result']['token']['token']
                self.usuario_id = response['result']['usuario']['id']
                self.token_expiry = datetime.now() + timedelta(hours=1)  # Assuming token is valid for 1 hour
                print(f"    Token retrieved. Exp: {response['result']['token']['expirationDate']}")
                print(f'    Usuario ID retrieved: {self.usuario_id}')
                self._fetch_empresa_id()  # Fetch client id after obtaining empresaId

    def _fetch_empresa_id(self):
        print('VITTE_CLIENT: Fetching empresa ID...')
        if self.usuario_id and not self.empresa_id:
            url = f'{self.base_url}/local/localesUsuario/{self.usuario_id}'
            response = self.session.get(url=url, headers=self._get_headers()).json()
            if 'result' in response:
                self.empresa_id = response['result'][0]['empresaId']
                print(f'    empresaId retrieved: {self.empresa_id}')
        else:
            print('VITTE_CLIENT: Saliendo de fetch empresa...')

    def _get_headers(self):
        self._fetch_token_and_usuario_id()  # Ensure token, empresaId and clientId are up to date
        return {
            'Authorization': f'Bearer {self.token}',
            'Accept': self.accept_str,
            'Accept-Encoding': self.encoding_str
        }

    # def _fetch_empresa_id(self):
    #     if not self.empresa_id:
    #         self._fetch_token_and_empresa_id()  # This ensures empresa_id is always updated with token
    #     return self.empresa_id