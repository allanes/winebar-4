from fastapi import APIRouter, HTTPException
from sql_app.api.fudo_integration import fudo_crud
from sql_app.api.fudo_integration.fudo_schemas import TablesResponse, SaleResponse

router = APIRouter()

@router.get("/tables", response_model=TablesResponse)
def read_tables():
    try:
        return fudo_crud.get_tables()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sales/{sale_id}", response_model=SaleResponse)
def read_sale(sale_id: str):
    try:
        return fudo_crud.get_sale_details(sale_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
