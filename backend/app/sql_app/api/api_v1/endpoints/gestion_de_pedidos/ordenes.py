from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sql_app import crud, schemas
from sql_app.api import deps

router = APIRouter()

@router.get("/{orden_id}", response_model=schemas.OrdenCompra)
def handle_read_orden_by_id(
    orden_id: int,
    db: Session = Depends(deps.get_db)
):
    orden_in_db = crud.orden.get(db=db, id=orden_id)
    if orden_in_db is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    return orden_in_db

@router.get("/by-rfid/{tarjeta_id}", response_model=schemas.OrdenCompra)
def handle_read_orden_by_client_rfid(
    tarjeta_id: int,
    db: Session = Depends(deps.get_db)
):
    orden_in_db = crud.orden.get_by_rfid(db=db, tarjeta_id=tarjeta_id)
    if orden_in_db is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    return orden_in_db

@router.get("/", response_model=List[schemas.OrdenCompra])
def handle_read_ordens(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    ordens = crud.orden.get_multi(db, skip=skip, limit=limit)
    # ordens = [orden for orden in ordens if orden.activa==True]
    return ordens

@router.post("/abrir", response_model=schemas.OrdenCompra)
def handle_abrir_orden(
    *,
    db: Session = Depends(deps.get_db),
    tarjeta_cliente: int
):
    ## REEMPLAZAR LA SIGUIENTE LINEA POR DEPS
    usuario_id = crud.personal_interno.get_multi(db=db, limit=1)[0].id
    ## 
    orden_in = schemas.OrdenCompraAbrir(
        abierta_por=usuario_id, 
        tarjeta_cliente=tarjeta_cliente)
    
    orden = crud.orden.abrir_orden(
        db = db, 
        abrir_orden_in = orden_in
    )

    if not orden:
        raise HTTPException(status_code=404, detail='No se pudo abrir el orden')
    
    return orden

@router.post("/cerrar", response_model=schemas.OrdenCompra)
def handle_cerrar_orden(
    *,
    tarjeta_cliente: int,
    db: Session = Depends(deps.get_db),
):
    ## REEMPLAZAR LA SIGUIENTE LINEA POR DEPS
    usuario_id = crud.personal_interno.get_multi(db=db, limit=1)[0].id
    ##
    orden_in = schemas.OrdenCompraCerrar(
        cerrada_por=usuario_id, 
        tarjeta_cliente=tarjeta_cliente)
    
    orden = crud.orden.cerrar_orden(
        db = db,
        orden_in = orden_in
    )

    if not orden:
        raise HTTPException(status_code=404, detail='La orden no se pudo abrir')
    
    return orden

@router.put("/{id}", response_model=schemas.OrdenCompra)
def handle_update_orden(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    orden_in: schemas.OrdenCompraUpdate
):
    orden = crud.orden.get(db=db, id=id)
    if not orden:
        raise HTTPException(status_code=404, detail=f"Persona no encontrada con DNI {id}")
    
    orden = crud.orden.update(
        db=db, db_obj=orden, obj_in=orden_in
    )
    return orden


