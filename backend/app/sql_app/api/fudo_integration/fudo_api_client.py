import requests
from datetime import datetime, timedelta
from typing import Optional
from sql_app.core.config import settings
from sql_app.api.fudo_integration.fudo_schemas import TablesResponse, SaleResponse

class FudoApiClientBase:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://api.fu.do/v1alpha1"
        self.token = None
        self.token_expiry = datetime.now()

    def _authenticate(self):
        print('Fudo: Setting up API key...')
        self.token = settings.FUDO_API_KEY
        print('Fudo: API key set successfully.')

    def _ensure_authentication(self):
        if self.token is None:
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
            return True, 'Health check passed: Successfully retrieved tables'
        except Exception as e:
            print(f'Health check failed: {str(e)}')
            return False, 'API health check failed'

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

fudo_api_client = FudoApiClientBase()
