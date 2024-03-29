from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sql_app import crud, schemas
from sql_app.api import deps

router = APIRouter()

@router.get("/con-tarjeta/{tarjeta_id}", response_model=schemas.ClienteOperaConTarjeta)
def handle_read_cliente_by_tarjeta_id(
    tarjeta_id: int,
    db: Session = Depends(deps.get_db)
):
    cliente_con_tarjeta_in_db = crud.cliente_opera_con_tarjeta.get_by_tarjeta_id(db=db, tarjeta_id=tarjeta_id)
    if cliente_con_tarjeta_in_db is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return cliente_con_tarjeta_in_db

@router.get("/{id}", response_model=schemas.Cliente)
def handle_read_cliente_by_id(
    id: int,
    db: Session = Depends(deps.get_db)
):
    cliente_in_db = crud.cliente.get(db=db, id=id)
    if cliente_in_db is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return cliente_in_db

@router.put("/{id}", response_model=schemas.Cliente)
def handle_update_cliente(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    cliente_in: schemas.ClienteUpdate
):
    cliente = crud.cliente.get(db=db, id=id)
    if not cliente:
        raise HTTPException(status_code=404, detail=f"Persona no encontrada con DNI {id}")
    
    cliente = crud.cliente.update(
        db=db, db_obj=cliente, obj_in=cliente_in
    )
    return cliente

@router.delete("/{id}", response_model=schemas.Cliente)
def handle_delete_cliente(
    *,
    db: Session = Depends(deps.get_db),
    id: int
):
    cliente, fue_creado, msj = crud.cliente.deactivate(db=db, id=id)
    if not fue_creado:
        raise HTTPException(status_code=404, detail=msj)
    
    return cliente

@router.get("/", response_model=List[schemas.ClienteWithDetails])
def handle_read_clientes(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    clientes_operan = crud.cliente_opera_con_tarjeta.get_multi(db, skip=skip, limit=limit)
    
    clientes_detallados = crud.cliente_opera_con_tarjeta.convertir_a_cliente_detallado(
        db=db, clientes_a_convertir=clientes_operan
    )
    
    return clientes_detallados

@router.post("/", response_model=schemas.Cliente)
def handle_create_cliente_with_tarjeta(
    *,
    db: Session = Depends(deps.get_db),
    tarjeta_id: int,
    cliente_in: schemas.ClienteCreate,
    detalle_adicional_in: schemas.DetallesAdicionalesForUI = None,
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)]
):
    print(f'usuario logueado id: {current_user.id}')
    cliente, fue_creado, error_msg = crud.cliente.create_with_tarjeta(
        db = db, 
        tarjeta_id = tarjeta_id,
        cliente_in = cliente_in,
        usuario_apertura_orden = current_user.id,
        detalles_adicionales_in = detalle_adicional_in,
    )

    if not fue_creado:
        raise HTTPException(status_code=404, detail=error_msg)
    
    return cliente

# @router.post("/entregar-tarjeta", response_model=schemas.Cliente)
# def handle_entregar_tarjeta(
#     *,
#     db: Session = Depends(deps.get_db),
#     asosiacion: schemas.ClienteYTarjeta
# ):
#     (cliente, pudo_entregarse, msg) = crud.cliente.entregar_tarjeta_a_personal(
#         db=db, 
#         personal_id=asosiacion.personal_id, 
#         tarjeta_id=asosiacion.tarjeta_id
#     )

#     if not pudo_entregarse:
#         raise HTTPException(status_code=404, detail=msg)
#     return cliente

# @router.post("/devolver-tarjeta", response_model=schemas.Tarjeta)
# def handle_devolver_tarjeta(
#     *,
#     db: Session = Depends(deps.get_db),
#     tarjeta_id: int
# ):
#     tarjeta_devuelta, fue_devuelta, msg = crud.cliente.personal_devuelve_tarjeta_a_banca(
#         db=db, tarjeta_id=tarjeta_id
#     )
#     if not fue_devuelta:
#         raise HTTPException(status_code=404, detail=msg)
#     return tarjeta_devuelta

