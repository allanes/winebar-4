import os
import sys
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sql_app import crud, schemas
from sql_app.api import deps
from sql_app.core.config import settings

router = APIRouter()

@router.get("/last", response_model=schemas.Configuracion)
def handle_get_last_configuracion(
    db: Session = Depends(deps.get_db)
):
    configuracion_in_db = crud.configuracion.get_last(db=db)
    if configuracion_in_db is None:
        raise HTTPException(status_code=404, detail="Configuracion no encontrada")
    print(f'configuracion encontrada: {configuracion_in_db.__dict__}')
    return configuracion_in_db

@router.get("/{id}", response_model=schemas.Configuracion)
def handle_read_configuracion_by_id(
    id: int,
    db: Session = Depends(deps.get_db)
):
    configuracion_in_db = crud.configuracion.get(db=db, id=id)
    if configuracion_in_db is None:
        raise HTTPException(status_code=404, detail="Configuracion no encontrada")
    
    return configuracion_in_db

# @router.delete("/{id}", response_model=schemas.Configuracion)
# def handle_delete_configuracion(
#     *,
#     db: Session = Depends(deps.get_db),
#     id: int
# ):
#     configuracion = crud.configuracion.remove(db=db, id=id)
#     if configuracion is None:
#         raise HTTPException(status_code=404, detail='')
    
#     return configuracion

@router.get("/", response_model=List[schemas.Configuracion])
def handle_read_configuracions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    configuracions = crud.configuracion.get_multi(db, skip=skip, limit=limit)
    # configuracions = [configuracion for configuracion in configuracions if configuracion.activa==True]
    return configuracions

@router.post("/", response_model=schemas.Configuracion)
def handle_create_configuracion(
    *,
    db: Session = Depends(deps.get_db),
    configuracion_in: schemas.ConfiguracionCreate,    
):
    configuracion = crud.configuracion.create(
        db = db, 
        obj_in=configuracion_in
    )

    if not configuracion:
        raise HTTPException(status_code=404, detail=f'No se pudo crear la configuracion')
    
    return configuracion
