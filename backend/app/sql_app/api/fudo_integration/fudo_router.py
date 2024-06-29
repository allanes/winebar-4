from fastapi import APIRouter, HTTPException, Query
from sql_app.api.fudo_integration import fudo_crud
from sql_app.api.fudo_integration.fudo_schemas import CustomTableResponse, SaleResponse

router = APIRouter()

@router.get("/mesas", response_model=CustomTableResponse)
def read_tables(only_active: bool = Query(True, description="Return only tables with active sales")):
    try:
        return fudo_crud.get_tables(only_active=only_active)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ventas/{sale_id}", response_model=SaleResponse)
def read_sale(sale_id: str):
    try:
        return fudo_crud.get_sale_details(sale_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
