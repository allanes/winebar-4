from fastapi import APIRouter, HTTPException, Query
from sql_app.api.fudo_integration import fudo_crud
from sql_app.api.fudo_integration.fudo_schemas import CustomTableResponse, SaleResponse, CustomSaleDetailResponse

router = APIRouter()

@router.get("/mesas", response_model=CustomTableResponse)
def read_tables(only_active: bool = Query(True, description="Return only tables with active sales")):
    try:
        mesas = fudo_crud.get_tables(only_active=only_active)
        # print(f'mesas recuperadas: {mesas}')
        return mesas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/ventas/por-mesa/{mesa_id}", response_model=list[CustomSaleDetailResponse])
def read_sales_by_mesa(mesa_id: int):
    try:
        mesas = fudo_crud.get_tables(only_active=True).data
        mesa = [mesa for mesa in mesas if mesa.id == mesa_id]
        if not mesa:
            raise HTTPException(status_code=500, detail=f'No se encontró mesa con id {mesa_id}')
        mesa = mesa[0]
        
        ventas = []
        for active_sale in mesa.activeSales.get('data', []):
            info_venta = fudo_crud.get_sale_details_custom(sale_id=active_sale.id)
            print(f'  venta agregada {active_sale}')
            ventas.append(info_venta)
        return ventas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ventas/{sale_id}", response_model=SaleResponse)
def read_sale(sale_id: str):
    try:
        return fudo_crud.get_sale_details(sale_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))