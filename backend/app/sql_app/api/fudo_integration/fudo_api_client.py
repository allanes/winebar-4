import requests
from datetime import datetime, timedelta
from typing import Optional
from sql_app.core.config import settings

class FudoApiClientBase:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://api.fu.do/v1alpha1"
        self.token = None
        self.token_expiry = datetime.now()

    def _authenticate(self):
        print('Fudo: Refreshing token...')
        headers = {
            "Authorization": f"Bearer {settings.FUDO_API_KEY}"
        }
        # For now, we're just setting the token to the API key
        # In a real-world scenario, you might want to exchange this for a session token
        self.token = settings.FUDO_API_KEY
        self.token_expiry = datetime.now() + timedelta(hours=1)
        print('Fudo: Authentication successful, token updated.')

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
        return response.json()

    def get_sale_details(self, sale_id: str):
        """Retrieve details of a specific sale"""
        url = f"{self.base_url}/sales/{sale_id}"
        response = self.session.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

fudo_api_client = FudoApiClientBase()
