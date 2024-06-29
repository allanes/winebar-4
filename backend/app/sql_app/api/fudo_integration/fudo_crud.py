from typing import List, Optional
from sql_app.api.fudo_integration.fudo_api_client import fudo_api_client
from sql_app.api.fudo_integration.fudo_schemas import SaleResponse, CustomTableResponse

def get_tables(only_active: bool = False) -> CustomTableResponse:
    """Retrieve the list of tables"""
    tables_response = fudo_api_client.get_tables()
    
    if only_active:
        active_tables = [table for table in tables_response.data if table.relationships.activeSales.get('data')]
        return CustomTableResponse(data=active_tables)
    
    return CustomTableResponse(data=tables_response.data)

def get_sale_details(sale_id: str) -> SaleResponse:
    """Retrieve details of a specific sale"""
    return fudo_api_client.get_sale_details(sale_id)
