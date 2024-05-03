from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sql_app import crud, schemas
from sql_app.api import deps

router = APIRouter()

@router.post("/informar-lector-tapa")
def handle_agregar_lector_tapa(
    *,
    db: Session = Depends(deps.get_db),
    lectores_disponibles: schemas.LectorTapaReceive,
    nombre_terminal_tapa_logueada: Annotated[str, Depends(deps.get_terminal_tapa_logueada)],
    check_turno_abierto: Annotated[bool, Depends(deps.check_turno_abierto)],
):
    print(f'Lectores recibidos: {len(lectores_disponibles.lista_lectores_disponibles)}')
    [print(f'   {lector}') for lector in lectores_disponibles.lista_lectores_disponibles]
    lectores_in_db = crud.lector_tapa.get_multi_by_terminal(
        db=db, 
        nombre_terminal=nombre_terminal_tapa_logueada
    )
    
    # Creo los lectores que no existian
    for nombre_lector_disponible in lectores_disponibles.lista_lectores_disponibles:
        if nombre_lector_disponible not in [lector.nombre_puerto for lector in lectores_in_db]:
            print(f'Creando nuevo lector de tapas: {nombre_lector_disponible}')
            crud.lector_tapa.create(
                db=db,
                obj_in=schemas.LectorTapaCreate(
                    nombre_terminal=nombre_terminal_tapa_logueada,
                    nombre_puerto=nombre_lector_disponible
                )
            )

    # Borro los lectores existentes pero no disponibles
    for lector_in_db in lectores_in_db:
        if lector_in_db.nombre_puerto not in [lector for lector in lectores_disponibles.lista_lectores_disponibles]:
            print(f'Borrando lector de tapas existente pero no disponible: {lector_in_db.nombre_puerto}')
            crud.lector_tapa.remove(db=db, id=lector_in_db.id)

# @router.put("/{id}", response_model=schemas.LectorTapa)
# def handle_update_lector_tapa(
#     *,
#     db: Session = Depends(deps.get_db),
#     id: int,
#     lector_tapa_in: schemas.LectorTapaUpdate
# ):
#     lector_tapa = crud.lector_tapa.get(db=db, id=id)
#     if not lector_tapa:
#         raise HTTPException(status_code=404, detail=f"Persona no encontrada con DNI {id}")
    
#     lector_tapa = crud.lector_tapa.update(
#         db=db, db_obj=lector_tapa, obj_in=lector_tapa_in
#     )
#     return lector_tapa

# @router.get("/{id}", response_model=schemas.LectorTapa)
# def handle_read_lectors_tapas_by_id(
#     id: int,
#     db: Session = Depends(deps.get_db)
# ):
#     lector_tapa_in_db = crud.lector_tapa.get(db=db, id=id)
#     if lector_tapa_in_db is None:
#         raise HTTPException(status_code=404, detail="LectorTapa no encontrado")
    
#     return lector_tapa_in_db

@router.get("/por-terminal", response_model=List[schemas.LectorTapa])
def handle_read_lectors_tapas_por_terminal(
    nombre_terminal_tapa_logueada: Annotated[str, Depends(deps.get_terminal_tapa_logueada)],
    db: Session = Depends(deps.get_db),
):
    lectores_tapas_para_terminal = crud.lector_tapa.get_multi_by_terminal(
        db=db,
        nombre_terminal=nombre_terminal_tapa_logueada
    )
    # lectors_tapas = [lector_tapa for lector_tapa in lectors_tapas if lector_tapa.activa==True]
    return lectores_tapas_para_terminal

@router.get("/", response_model=List[schemas.LectorTapa])
def handle_read_lectors_tapas(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    lectors_tapas = crud.lector_tapa.get_multi(db, skip=skip, limit=limit)
    # lectors_tapas = [lector_tapa for lector_tapa in lectors_tapas if lector_tapa.activa==True]
    return lectors_tapas