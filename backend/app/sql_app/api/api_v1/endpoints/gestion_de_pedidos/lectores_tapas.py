from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sql_app import crud, schemas
from sql_app.api import deps

router = APIRouter()

@router.post("/agregar-lector-tapa")
def handle_agregar_lector_tapa(
    *,
    db: Session = Depends(deps.get_db),
    lectores_disponibles: schemas.LectorTapaReceive,
    nombre_terminal_logueada: Annotated[schemas.PersonalInterno, Depends(deps.get_terminal_logueada)],
    check_turno_abierto: Annotated[bool, Depends(deps.check_turno_abierto)],
):
    print(f'Terminal logueada: {nombre_terminal_logueada}')
    print(f'Lectores recibidos: {len(lectores_disponibles.lista_lectores_disponibles)}')
    [print(f'   {lector}') for lector in lectores_disponibles.lista_lectores_disponibles]
    # print(f'usuario logueado id: {current_user.id}')
    # print(f'Agregando tapa por id: {renglon_in.lector_tapa_id}')
    # renglon_in_db, fue_agregado, msg = crud.lector_tapa.create(
    #     db=db,
    #     obj_in=lector_in
    # )

    # if not fue_agregado:
    #     raise HTTPException(status_code=404, detail=msg)
    
    # lector_tapa = crud.lector_tapa.get_lector_tapa_abierto_por_tarjeta(db=db, tarjeta_id=tarjeta_cliente)
    
    # return lector_tapa
    pass

@router.post("/agregar-lector_tapa-by-phys", response_model=schemas.LectorTapa)
def handle_agregar_lector_tapa_by_phys(
    *,
    tarjeta_cliente: int, 
    phys_port: str,
    db: Session = Depends(deps.get_db),
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)],
    check_turno_abierto: Annotated[bool, Depends(deps.check_turno_abierto)],
):
    print(f'usuario logueado id: {current_user.id}')
    print(f'puerto a chequear: {phys_port}')
    
    mapa_puertos_a_tapas = {
        "usb-0000:01:00.0-1.1.3/input0": 1,
        "usb-0000:01:00.0-1.1.2/input0": 2
    }
    renglon_in = schemas.RenglonCreate(
        cantidad=1,
        lector_tapa_id=mapa_puertos_a_tapas.get(phys_port)
    )

    if not renglon_in.lector_tapa_id:
        raise HTTPException(status_code=404, detail=msg)
    
    print(f'Agregando tapa por id: {renglon_in.lector_tapa_id}')

    renglon_in_db, fue_agregado, msg = crud.lector_tapa.agregar_lector_tapa_a_lector_tapa(
        db=db,
        renglon_in=renglon_in,
        atendido_por=current_user.id,
        tarjeta_cliente=tarjeta_cliente
    )

    if not fue_agregado:
        raise HTTPException(status_code=404, detail=msg)
    
    print(f'renglon cambiado: {renglon_in_db.__dict__}')
    lector_tapa = crud.lector_tapa.get_lector_tapa_abierto_por_tarjeta(db=db, tarjeta_id=tarjeta_cliente)
    
    return lector_tapa

@router.put("/{id}", response_model=schemas.LectorTapa)
def handle_update_lector_tapa(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    lector_tapa_in: schemas.LectorTapaUpdate
):
    lector_tapa = crud.lector_tapa.get(db=db, id=id)
    if not lector_tapa:
        raise HTTPException(status_code=404, detail=f"Persona no encontrada con DNI {id}")
    
    lector_tapa = crud.lector_tapa.update(
        db=db, db_obj=lector_tapa, obj_in=lector_tapa_in
    )
    return lector_tapa

@router.get("/{id}", response_model=schemas.LectorTapa)
def handle_read_lectors_tapas_by_id(
    id: int,
    db: Session = Depends(deps.get_db)
):
    lector_tapa_in_db = crud.lector_tapa.get(db=db, id=id)
    if lector_tapa_in_db is None:
        raise HTTPException(status_code=404, detail="LectorTapa no encontrado")
    
    return lector_tapa_in_db

@router.get("/", response_model=List[schemas.LectorTapa])
def handle_read_lectors_tapas(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    lectors_tapas = crud.lector_tapa.get_multi(db, skip=skip, limit=limit)
    # lectors_tapas = [lector_tapa for lector_tapa in lectors_tapas if lector_tapa.activa==True]
    return lectors_tapas