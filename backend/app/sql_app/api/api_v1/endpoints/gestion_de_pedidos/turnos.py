from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sql_app import crud, schemas
from sql_app.api import deps

router = APIRouter()

@router.post("/abrir", response_model=schemas.Turno)
def handle_abrir_turno(
    *,
    db: Session = Depends(deps.get_db),
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)]
):
    print(f'usuario logueado id: {current_user.id}')
    turno_in = schemas.TurnoCreate(abierto_por=current_user.id)

    turno_abierto = crud.turno.get_open_turno(db=db)
    if turno_abierto is not None:
        raise HTTPException(status_code=404, detail='Ya existe un turno abierto')    
    
    turno = crud.turno.abrir_turno(
        db = db, 
        turno_in = turno_in
    )

    if not turno:
        raise HTTPException(status_code=404, detail='No se pudo abrir el turno')
    
    return turno

@router.post("/cerrar", response_model=schemas.Turno)
def handle_cerrar_turno(
    *,
    db: Session = Depends(deps.get_db),
    info_de_cierre: schemas.InfoDeCierre,
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)],
    check_turno_abierto: Annotated[bool, Depends(deps.check_turno_abierto)],
):
    print(f'usuario logueado id: {current_user.id}')
    turno, pudo_cerrarse, msg = crud.turno.cerrar_turno(
        db = db,
        cerrado_por = current_user.id,
        info_de_cierre=info_de_cierre
    )

    if not pudo_cerrarse:
        raise HTTPException(status_code=404, detail=msg)
    
    return turno

@router.post("/cambiar-cajero", response_model=schemas.Turno)
def handle_cambiar_cajero(
    *,
    db: Session = Depends(deps.get_db),
    info_de_cierre: schemas.InfoDeCierre,
    nuevo_cajero_rfid: int,
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)],
    check_turno_abierto: Annotated[bool, Depends(deps.check_turno_abierto)],
):
    usuario_id_apertura_turno = crud.turno.get_open_turno(db=db).abierto_por
    usuario_apertura_in_db = crud.personal_interno.get_active(db=db, id=usuario_id_apertura_turno)
    if current_user.id != usuario_id_apertura_turno:
        raise HTTPException(status_code=404, detail=f'El turno debe ser cerrado por el usuario {usuario_apertura_in_db.nombre}. (Usuario actual: {current_user.nombre})')

    nuevo_cajero_in_db = crud.personal_interno.get_by_rfid(db=db, tarjeta_id=nuevo_cajero_rfid)
    if nuevo_cajero_in_db is None or not nuevo_cajero_in_db.activa:
        raise HTTPException(status_code=404, detail='No se encontró personal habilitado con esa tarjeta')

    turno, pudo_cerrarse, msg = crud.turno.cambiar_cajero(
        db = db,
        cerrado_por = current_user.id,
        info_de_cierre=info_de_cierre,
        nuevo_cajero_id=nuevo_cajero_in_db.id
    )

    if not pudo_cerrarse:
        raise HTTPException(status_code=404, detail=msg)
    
    return turno

@router.get('/turno-en-curso', response_model=schemas.Turno)
def handle_get_turno_abierto(*,
    db: Session = Depends(deps.get_db),
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)],
    check_turno_abierto: Annotated[bool, Depends(deps.check_turno_abierto)],
):
    turno_en_curso = crud.turno.get_open_turno(db=db)
    if not turno_en_curso:
        raise HTTPException(status_code=404, detail='No se encontró un turno abierto')
    
    return turno_en_curso

@router.get("/{id}", response_model=schemas.Turno)
def handle_read_turno_by_id(
    id: int,
    db: Session = Depends(deps.get_db)
):
    turno_in_db = crud.turno.get(db=db, id=id)
    if turno_in_db is None:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    
    return turno_in_db

@router.get("/", response_model=List[schemas.Turno])
def handle_read_turnos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    turnos = crud.turno.get_multi(db, skip=skip, limit=limit)
    # turnos = [turno for turno in turnos if turno.activa==True]
    return turnos

