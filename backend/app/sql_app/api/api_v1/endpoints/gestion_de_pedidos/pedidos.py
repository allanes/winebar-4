from typing import List, Annotated

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
    pedidos_in_db = crud.pedido.get_pedidos_por_tarjeta(db=db, tarjeta_id=tarjeta_id)
    return pedidos_in_db

@router.post("/abrir", response_model=schemas.Pedido)
def handle_abrir_pedido(
    *,
    tarjeta_cliente: int, 
    db: Session = Depends(deps.get_db),
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)]
):
    print(f'usuario logueado id: {current_user.id}')
    pedido_in = schemas.PedidoCreate(atendido_por=current_user.id)
    
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
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)]
):
    print(f'usuario logueado id: {current_user.id}')
    renglon_in_db, fue_agregado, msg = crud.pedido.agregar_producto_a_pedido(
        db=db,
        renglon_in=renglon_in,
        atendido_por=current_user.id,
        tarjeta_cliente=tarjeta_cliente
    )

    if not fue_agregado:
        raise HTTPException(status_code=404, detail=msg)
    
    return renglon_in_db

@router.post("/quitar-producto", response_model=schemas.Renglon)
def handle_quitar_renglon(
    *,
    tarjeta_cliente: int, 
    producto_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)]
):
    print(f'usuario logueado id: {current_user.id}')
    renglon_removido_in_db, fue_quitado, msg = crud.pedido.quitar_producto_de_pedido(
        db=db,
        producto_id=producto_id,
        tarjeta_cliente=tarjeta_cliente
    )

    if not fue_quitado:
        raise HTTPException(status_code=404, detail=msg)
    
    return renglon_removido_in_db

@router.post("/cerrar", response_model=schemas.Pedido)
def handle_cerrar_pedido(
    *,
    tarjeta_cliente: int, 
    db: Session = Depends(deps.get_db),
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)]
):
    print(f'usuario logueado id: {current_user.id}')
    pedido, pudo_cerrarse, msg = crud.pedido.cerrar_pedido(
        db = db,
        cerrado_por = current_user.id,
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