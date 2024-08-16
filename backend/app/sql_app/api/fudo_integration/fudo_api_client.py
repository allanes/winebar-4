import requests
from datetime import datetime, timedelta
from typing import Optional
from sql_app.core.config import settings
from sql_app.api.fudo_integration.fudo_schemas import TablesResponse, SaleResponse, RoomsResponse, FUDO_ITEM_CREATE__MOCK_RESPONSE

class FudoApiClientBase:
    def __init__(self, is_production: bool = True):
        self.session = requests.Session()
        self.base_url = "https://api.fu.do/v1alpha1"
        self.auth_url = "https://auth.fu.do/api" if is_production else "https://auth-staging.fu.do/api"
        self.api_key = settings.FUDO_API_KEY
        self.api_secret = settings.FUDO_API_SECRET
        self.token = None
        self.token_expiry = datetime.now()

    def _authenticate(self):
        print('Fudo: Authenticating...')
        payload = {
            "apiKey": self.api_key,
            "apiSecret": self.api_secret
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        response = self.session.post(self.auth_url, json=payload, headers=headers)
        response.raise_for_status()
        auth_data = response.json()
        self.token = auth_data["token"]
        self.token_expiry = datetime.fromtimestamp(auth_data["exp"])
        print('Fudo: Authentication successful.')

    def _ensure_authentication(self):
        if self.token is None or datetime.now() >= self.token_expiry:
            self._authenticate()

    def _get_headers(self):
        self._ensure_authentication()
        return {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/json'
        }

    def check_health(self) -> tuple[bool, str]:
        """
        Checks the health of the Fudo API service by trying to fetch the tables.
        This ensures the API is responsive and the authentication is valid.
        """
        try:
            self._ensure_authentication()
            self.get_tables()
            return True, 'Fudo Health check passed: Successfully retrieved tables'
        except Exception as e:
            print(f'Fudo Health check failed: {str(e)}')
            return False, 'Fudo API health check failed'

    def get_tables(self):
        """Retrieve the list of tables"""
        url = f"{self.base_url}/tables"
        params = {"include": "activeSales"}
        response = self.session.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        return TablesResponse(**response.json())

    def get_sale_details(self, sale_id: str):
        """Retrieve details of a specific sale"""
        url = f"{self.base_url}/sales/{sale_id}"
        response = self.session.get(url, headers=self._get_headers())
        response.raise_for_status()
        return SaleResponse(**response.json())
    
    def get_rooms(self):
        """Retrieve the list of rooms"""
        url = f"{self.base_url}/rooms"
        response = self.session.get(url, headers=self._get_headers())
        response.raise_for_status()
        return RoomsResponse(**response.json())
    
    def create_item(self, payload: dict, mock=False):
        """Create a new item in Fudo"""
        if mock:
            print(f'Mock de creacion de item en FUDO para exportar orden:')
            print(f'    {payload=}')
            return FUDO_ITEM_CREATE__MOCK_RESPONSE
        
        url = f"{self.base_url}/items"
        response = self.session.post(url, headers=self._get_headers(), json=payload)
        # print(f'FUDO: respuesta al crear consumo: {response=}')
        response.raise_for_status()
        return response
    
fudo_api_client = FudoApiClientBase()
