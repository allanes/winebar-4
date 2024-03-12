from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sql_app import crud, schemas
from sql_app.api import deps

router = APIRouter()

@router.get("/{id}", response_model=schemas.Tarjeta)
def read_tarjeta_by_id(
    id: int,
    db: Session = Depends(deps.get_db)
):
    tarjeta_in_db = crud.tarjeta.get(db=db, id=id)
    if tarjeta_in_db is None:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    
    return tarjeta_in_db

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
    tarjeta, fue_borrada, msg = crud.tarjeta.deactivate(db=db, id=id)
    if not fue_borrada:
        raise HTTPException(status_code=404, detail=msg)
    return tarjeta

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
    tarjeta, fue_creada, msg = crud.tarjeta.create_or_reactivate(db=db, obj_in=tarjeta_in)
    if not fue_creada:
        raise HTTPException(status_code=404, detail=msg)
    
    return tarjeta
