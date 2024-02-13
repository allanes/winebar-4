from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sql_app import crud, schemas
from sql_app.api import deps

router = APIRouter()

@router.get("/{tarjeta_id}", response_model=schemas.Tarjeta)
def read_tarjeta_by_id(
    tarjeta_id: int,
    db: Session = Depends(deps.get_db)
):
    tarjeta_in_db = crud.tarjeta.get(db=db, id=tarjeta_id)
    if tarjeta_in_db is None:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    
    return tarjeta_in_db

@router.get("/", response_model=List[schemas.Tarjeta])
def read_tarjetas(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    tarjetas = crud.tarjeta.get_multi(db, skip=skip, limit=limit)
    # tarjetas = [tarjeta for tarjeta in tarjetas if tarjeta.activa==True]
    return tarjetas

@router.post("/", response_model=schemas.Tarjeta)
def create_tarjeta(
    *,
    db: Session = Depends(deps.get_db),
    tarjeta_in: schemas.TarjetaCreate
):
    rol_en_db = crud.rol.get_by_name(db=db, name=tarjeta_in.rol_nombre)
    if not rol_en_db:
        raise HTTPException(status_code=404, detail=f"Rol '{tarjeta_in.rol_nombre}' no encontrado")
    
    try:
        preexiste_tarjeta = crud.tarjeta.get_by_raw_rfid(db=db, raw_rfid=tarjeta_in.raw_rfid)
        if preexiste_tarjeta:
            raise HTTPException(status_code=400, detail=f"La tarjeta ya existe")
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Tarjeta inválida")
    
    tarjeta = crud.tarjeta.create(db=db, obj_in=tarjeta_in)
    
    return tarjeta

@router.put("/{id}", response_model=schemas.Tarjeta)
def update_tarjeta(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    tarjeta_in: schemas.TarjetaUpdate
):
    tarjeta = crud.tarjeta.get(db=db, id=id)
    if not tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    tarjeta = crud.tarjeta.update(db=db, db_obj=tarjeta, obj_in=tarjeta_in)
    return tarjeta

@router.delete("/{id}", response_model=schemas.Tarjeta)
def delete_tarjeta(
    *,
    db: Session = Depends(deps.get_db),
    id: int
):
    tarjeta = crud.tarjeta.get(db=db, id=id)
    if not tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    tarjeta = crud.tarjeta.remove(db=db, id=id)
    return tarjeta
