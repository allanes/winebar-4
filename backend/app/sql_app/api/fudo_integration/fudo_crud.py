from typing import List, Optional
from sql_app.api.fudo_integration.fudo_api_client import fudo_api_client
from sql_app.api.fudo_integration.fudo_schemas import SaleResponse, CustomTableResponse, MesaFudoCustom, CustomSaleDetailResponse

def get_tables(only_active: bool = False) -> CustomTableResponse:
    """Retrieve the list of tables"""
    tables_response = fudo_api_client.get_tables()
    
    if only_active:
        tables_response = [table for table in tables_response.data if table.relationships.activeSales.get('data')]
    
    mesas_custom = []
    for mesa in tables_response:
        room_data = mesa.relationships.room.get('data', None)
        active_sales = mesa.relationships.activeSales
        # print(f'fudo room data: {room_data}')
        mesa_fudo = MesaFudoCustom(
            id=mesa.id,
            number=mesa.attributes.number,
            room_id=room_data.id,
            # room_name=
            cant_ventas=len(active_sales.get('data', None)),
            activeSales=active_sales
        )
        mesas_custom.append(mesa_fudo)

    return CustomTableResponse(data=mesas_custom)

def get_sale_details(sale_id: str) -> SaleResponse:
    """Retrieve details of a specific sale"""
    return fudo_api_client.get_sale_details(sale_id)

def get_sale_details_custom(sale_id: str) -> CustomSaleDetailResponse:
    """Retrieve details of a specific sale"""
    venta = fudo_api_client.get_sale_details(sale_id).data
    print(f'{venta.attributes.saleType=}, {venta.type=}')
    customer_name = venta.attributes.customerName if venta.attributes.customerName else None
    
    venta_custom = CustomSaleDetailResponse(
        id = venta.id,
        type=venta.type,
        createdAt=venta.attributes.createdAt,
        people=venta.attributes.people,
        customerName=customer_name,
        total=venta.attributes.total,
        saleState=venta.attributes.saleState
    )
    
    return venta_custom