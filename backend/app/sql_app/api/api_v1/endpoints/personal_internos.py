from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sql_app import crud, schemas
from sql_app.api import deps

router = APIRouter()

@router.get("/{personal_interno_id}", response_model=schemas.PersonalInterno)
def read_personal_interno_by_id(
    personal_interno_id: int,
    db: Session = Depends(deps.get_db)
):
    personal_interno_in_db = crud.personal_interno.get(db=db, id=personal_interno_id)
    if personal_interno_in_db is None:
        raise HTTPException(status_code=404, detail="Personal no encontrado")
    
    return personal_interno_in_db

@router.get("/", response_model=List[schemas.PersonalInterno])
def read_personal_internos(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    personal_internos = crud.personal_interno.get_multi(db, skip=skip, limit=limit)
    # personal_internos = [personal_interno for personal_interno in personal_internos if personal_interno.activa==True]
    return personal_internos

@router.post("/", response_model=schemas.PersonalInterno)
def create_personal_interno(
    *,
    db: Session = Depends(deps.get_db),
    personal_interno_in: schemas.PersonalInternoCreate,
    tarjeta_id: int
):
    personal_interno_in.tarjeta_id = tarjeta_id
    puede_crearse, msg = crud.personal_interno.check_puede_ser_creada(db=db, personal_interno_in=personal_interno_in)
    if not puede_crearse:
        raise HTTPException(status_code=404, detail=msg)
    
    personal_interno = crud.personal_interno.create(db=db, obj_in=personal_interno_in)
    
    return personal_interno

@router.put("/{id}", response_model=schemas.PersonalInterno)
def update_personal_interno(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    personal_interno_in: schemas.PersonalInternoUpdate
):
    personal_interno = crud.personal_interno.get(db=db, id=id)
    if not personal_interno:
        raise HTTPException(status_code=404, detail=f"Persona no encontrada con DNI {id}")
    
    personal_interno = crud.personal_interno.update(db=db, db_obj=personal_interno, obj_in=personal_interno_in)
    return personal_interno

@router.delete("/{id}", response_model=schemas.PersonalInterno)
def delete_personal_interno(
    *,
    db: Session = Depends(deps.get_db),
    id: int
):
    puede_borrarse, msg = crud.personal_interno.check_puede_ser_borrada(db=db, personal_interno_id=id)
    if not puede_borrarse:
        raise HTTPException(status_code=404, detail=msg)
    
    personal_interno = crud.personal_interno.remove(db=db, id=id)
    return personal_interno
