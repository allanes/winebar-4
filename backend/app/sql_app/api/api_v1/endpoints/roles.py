from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sql_app import crud, schemas
from sql_app.api import deps

router = APIRouter()

@router.get("/{rol_id}", response_model=schemas.Rol)
def read_rol_by_id(
    rol_id: int,
    db: Session = Depends(deps.get_db)
):
    rol_in_db = crud.rol.get(db=db, id=rol_id)
    if rol_in_db is None:
        raise HTTPException(status_code=404, detail="Rol no encontrada")
    
    return rol_in_db

@router.get("/", response_model=List[schemas.Rol])
def read_roles(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    roles = crud.rol.get_multi(db, skip=skip, limit=limit)
    # roles = [rol for rol in roles if rol.activa==True]
    return roles

@router.post("/", response_model=schemas.Rol)
def create_rol(
    *,
    db: Session = Depends(deps.get_db),
    rol_in: schemas.RolCreate
):
    rol = crud.rol.create(db=db, obj_in=rol_in)
    return rol

@router.put("/{id}", response_model=schemas.Rol)
def update_rol(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    rol_in: schemas.RolUpdate
):
    rol = crud.rol.get(db=db, id=id)
    if not rol:
        raise HTTPException(status_code=404, detail="Rol not found")
    rol = crud.rol.update(db=db, db_obj=rol, obj_in=rol_in)
    return rol

@router.delete("/{id}", response_model=schemas.Rol)
def delete_rol(
    *,
    db: Session = Depends(deps.get_db),
    id: int
):
    rol = crud.rol.get(db=db, id=id)
    if not rol:
        raise HTTPException(status_code=404, detail="Rol not found")
    rol = crud.rol.remove(db=db, id=id)
    return rol
