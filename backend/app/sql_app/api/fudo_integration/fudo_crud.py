import os
import json
from typing import List, Optional
from fastapi.templating import Jinja2Templates
from sql_app.core.config import settings
from sql_app.api.fudo_integration.fudo_api_client import fudo_api_client
from sql_app.api.fudo_integration.fudo_schemas import (
    SaleResponse, 
    CustomTableResponse, 
    MesaFudoCustom, 
    CustomSaleDetailResponse,
    FudoExportRequest,
    FudoExportItem,
    FUDO_PRODUCT_IDS
)

templates = Jinja2Templates(directory=settings.TEMPLATES_PATH)
fudo_item_post_template_filename = 'fudo_item_post_body.txt'

def get_tables(only_active: bool = False) -> CustomTableResponse:
    """Retrieve the list of tables"""
    tables_response = fudo_api_client.get_tables()
    rooms_info = fudo_api_client.get_rooms().data
    
    if only_active:
        tables_response = [table for table in tables_response.data if table.relationships.activeSales.get('data')]
    
    mesas_custom = []
    for mesa in tables_response:
        room_data = mesa.relationships.room.get('data', None)
        room_metadata = [room_info for room_info in rooms_info if room_info.id == int(room_data.id)]
        # print(f'room metadata: {room_metadata}')
        room_metadata = room_metadata[0] if room_metadata else {}
        active_sales = mesa.relationships.activeSales
        # print(f'fudo room data: {room_data}')
        mesa_fudo = MesaFudoCustom(
            id=mesa.id,
            number=mesa.attributes.number,
            room_id=room_data.id,
            room_name=room_metadata.attributes.name,
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
        total=f'$ {venta.attributes.total:.2f}',
        saleState=venta.attributes.saleState
    )
    
    return venta_custom

def export_items_to_fudo(export_request: FudoExportRequest, mock = False) -> bool:
    # mock = True
    try:
        for item in export_request.items:
            payload = _prepare_fudo_item_payload(item)
            response = fudo_api_client.create_item(payload, mock=mock)

            if not mock:
                if not (response.status_code >= 200 and response.status_code < 300):
                    print(f"Error exporting item to Fudo: {response.text}")
                    print(f"    request payload: {payload}")
                    return False
        return True
    except Exception as e:
        print(f"Error exporting items to Fudo: {str(e)}")
        return False

def _prepare_fudo_item_payload(item: FudoExportItem) -> dict:
    rendered_payload = templates.get_template(fudo_item_post_template_filename).render(
        comment=f"Orden {item.order_id}: {item.comment}",
        price=item.amount,
        quantity=item.quantity,
        product_id=FUDO_PRODUCT_IDS[item.type],
        sale_id=item.sale_id
    )
    return json.loads(rendered_payload)