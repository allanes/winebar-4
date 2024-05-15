from functools import lru_cache
from typing import Optional
from datetime import datetime, timedelta
import json
import requests
from sql_app.core.config import settings

class VitteApiClientBase():
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://app.vitte.com.ar/api"
        self.empresa_id = None
        self.local_id = None
        self.client_id = None
        self.token = None
        self.token_expiry = datetime.now()
        self._setup_login_details()

    def _setup_login_details(self):
        # Initialize from environment variables or configuration
        self.login_details = {
            'clave': settings.VITTE_CLAVE,
            'server': settings.VITTE_SERVER,
            'usuario': settings.VITTE_USUARIO,
            'validate': "",
        }

    def _fetch_initial_state(self):
        self._authenticate()
        self._fetch_empresa_id()

    def _authenticate(self):
        print('Vitte: Refreshing token...')
        response = self.session.post(f'{self.base_url}/seguridad/login', json=self.login_details).json()
        if response.get('result', {}).get('token'):
            self.token = response['result']['token']['token']
            self.token_expiry = datetime.now() + timedelta(hours=1)
            self.client_id = response['result']['usuario']['id']  # Assuming client ID is part of the login result
            print('Vitte:   Authentication successful, client and token updated.')
        else:
            print('Vitte:   Authentication failed.')

    def _fetch_empresa_id(self):
        if not self.client_id:
            raise ValueError("Client ID must be available to fetch empresa ID.")
        empresa_url = f'{self.base_url}/local/localesUsuario/{self.client_id}'
        response = self.session.get(url=empresa_url, headers=self._get_headers()).json()
        if 'result' in response and len(response['result']) > 0:
            self.empresa_id = response['result'][0]['empresaId']
            self.local_id = response['result'][0]['id']
            print(f'Vitte:  Empresa ID fetched: {self.empresa_id}')
        else:
            print('Vitte:   Failed to fetch Empresa ID.')

    def _ensure_authentication(self):
        if self.token is None or datetime.now() >= self.token_expiry:
            self._authenticate()

    def _get_headers(self):
        self._ensure_authentication()
        return {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br'
        }

    def check_health(self) -> tuple[bool, str]:
        """
        Checks the health of the Vitte API service by trying to fetch the empresa ID.
        This ensures the API is responsive and the authentication is valid.
        """
        try:
            self._ensure_authentication()  # Ensure the API is authenticated before the check
            self._fetch_empresa_id()       # Attempt to fetch the empresa ID as a health check
            return True, f'Health check passed: Connected to Empresa ID {self.empresa_id}'
        except Exception as e:
            # Handle any exceptions that may occur during the health check
            print(f'Health check failed: {str(e)}')
            return False, 'API health check failed'
