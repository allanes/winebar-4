from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sql_app import crud, schemas
from sql_app.api import deps

router = APIRouter()

@router.get("/by-rfid/{tarjeta_id}", response_model=schemas.Pedido)
def handle_read_pedido_by_rfid(
    tarjeta_id: int,
    db: Session = Depends(deps.get_db)
):
    pedidos_in_db = crud.pedido.get_by_rfid(db=db, tarjeta_id=tarjeta_id)
    return pedidos_in_db

@router.post("/abrir", response_model=schemas.Pedido)
def handle_abrir_pedido(
    *,
    tarjeta_cliente: int, 
    db: Session = Depends(deps.get_db),   
):
    ## REEMPLAZAR LA SIGUIENTE LINEA POR DEPS
    usuario_id = crud.personal_interno.get_multi(db=db, limit=1)[0].id
    ## 
    pedido_in = schemas.PedidoCreate(atendido_por=usuario_id)
    
    pedido, pudo_abrirse, msg = crud.pedido.abrir_pedido(
        db = db, 
        pedido_in = pedido_in,
        tarjeta_cliente=tarjeta_cliente
    )

    if not pudo_abrirse:
        raise HTTPException(status_code=404, detail=msg)
    
    return pedido

@router.post("/agregar-producto", response_model=schemas.Renglon)
def handle_agregar_producto(
    *,
    tarjeta_cliente: int, 
    renglon_in: schemas.RenglonCreate,
    db: Session = Depends(deps.get_db),    
):
    ## REEMPLAZAR LA SIGUIENTE LINEA POR DEPS
    usuario_id = crud.personal_interno.get_multi(db=db, limit=1)[0].id
    ##

    renglon_in_db, fue_agregado, msg = crud.pedido.agregar_producto_a_renglon(
        db=db,
        renglon_in=renglon_in,
        atendido_por=usuario_id,
        tarjeta_cliente=tarjeta_cliente
    )

    if not fue_agregado:
        raise HTTPException(status_code=404, detail=msg)
    
    return renglon_in_db

@router.post("/cerrar", response_model=schemas.Pedido)
def handle_cerrar_pedido(
    *,
    tarjeta_cliente: int, 
    db: Session = Depends(deps.get_db),    
):
    ## REEMPLAZAR LA SIGUIENTE LINEA POR DEPS
    usuario_id = crud.personal_interno.get_multi(db=db, limit=1)[0].id
    ##
    
    pedido, pudo_cerrarse, msg = crud.pedido.cerrar_pedido(
        db = db,
        cerrado_por = usuario_id,
        tarjeta_cliente=tarjeta_cliente
    )

    if not pudo_cerrarse:
        raise HTTPException(status_code=404, detail=msg)
    
    return pedido

@router.put("/{id}", response_model=schemas.Pedido)
def handle_update_pedido(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    pedido_in: schemas.PedidoUpdate
):
    pedido = crud.pedido.get(db=db, id=id)
    if not pedido:
        raise HTTPException(status_code=404, detail=f"Persona no encontrada con DNI {id}")
    
    pedido = crud.pedido.update(
        db=db, db_obj=pedido, obj_in=pedido_in
    )
    return pedido

@router.get("/{id}", response_model=schemas.Pedido)
def handle_read_pedidos_by_id(
    id: int,
    db: Session = Depends(deps.get_db)
):
    pedido_in_db = crud.pedido.get(db=db, id=id)
    if pedido_in_db is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    return pedido_in_db

@router.get("/", response_model=List[schemas.Pedido])
def handle_read_pedidos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    pedidos = crud.pedido.get_multi(db, skip=skip, limit=limit)
    # pedidos = [pedido for pedido in pedidos if pedido.activa==True]
    return pedidos