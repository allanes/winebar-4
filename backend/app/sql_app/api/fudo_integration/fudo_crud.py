from typing import List
from sql_app.api.fudo_integration.fudo_api_client import fudo_api_client
from sql_app.api.fudo_integration.fudo_schemas import TablesResponse, SaleResponse

def get_tables() -> TablesResponse:
    """Retrieve the list of tables"""
    return fudo_api_client.get_tables()

def get_sale_details(sale_id: str) -> SaleResponse:
    """Retrieve details of a specific sale"""
    return fudo_api_client.get_sale_details(sale_id)
