import os
import sys
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from sql_app import crud, schemas
from sql_app.api import deps
from sql_app.core.config import settings

router = APIRouter()

@router.post("/foto/{id}", response_model=schemas.Tapa)
def handle_upload_foto(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    foto: UploadFile = File(...)
):
    tapa = crud.tapa.get(db=db, id=id)
    if not tapa:
        raise HTTPException(status_code=404, detail=f"Tapa no encontrada con ID {id}")
    
    # Save the uploaded file and update the tapa's foto field
    filename = crud.tapa.get_tapa_image_name(tapa_in_db=tapa)  # Generate a unique filename
    file_path = f"{settings.IMAGES_PATH}/{filename}"  # Specify the path to save the file
    print(f'ruta de imagenes: {os.path.abspath(settings.IMAGES_PATH)}')

    if not os.path.exists(settings.IMAGES_PATH):
        os.mkdir(settings.IMAGES_PATH)
        
    with open(file_path, "wb") as file:
        file.write(foto.file.read())
    
    tapa = crud.tapa.update_image_field(db=db, id=id)
    return tapa

@router.get("/foto/{id}", response_class=FileResponse)
def handle_get_foto(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    by_product_id: bool = False
):
    tapa = None
    if by_product_id:
        tapa = crud.tapa.get_by_product_id(db=db, producto_id=id)
    else:
        tapa = crud.tapa.get(db=db, id=id)
    if not tapa:
        raise HTTPException(status_code=404, detail=f"Tapa no encontrada con ID {id}")
    
    if not tapa.foto:
        raise HTTPException(status_code=404, detail=f"Foto no encontrada para Tapa con ID {id}")
    
    file_path = f"{settings.IMAGES_PATH}/{tapa.foto}"  # Specify the path where the file is saved
    return file_path

@router.get("/{id}", response_model=schemas.Tapa)
def handle_read_tapa_by_id(
    id: int,
    db: Session = Depends(deps.get_db)
):
    tapa_in_db = crud.tapa.get(db=db, id=id)
    if tapa_in_db is None:
        raise HTTPException(status_code=404, detail="Tapa no encontrada")
    
    return tapa_in_db

@router.put("/{id}", response_model=schemas.Tapa)
def handle_update_tapa(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    tapa_in: schemas.TapaUpdate
):
    tapa = crud.tapa.get(db=db, id=id)
    if not tapa:
        raise HTTPException(status_code=404, detail=f"Tapa no encontrada con id {id}")
    
    tapa = crud.tapa.update(
        db=db, db_obj=tapa, obj_in=tapa_in
    )
    return tapa

@router.delete("/{id}", response_model=schemas.Tapa)
def handle_delete_tapa(
    *,
    db: Session = Depends(deps.get_db),
    id: int
):
    tapa = crud.tapa.remove(db=db, id=id)
    if tapa is None:
        raise HTTPException(status_code=404, detail='')
    
    return tapa

@router.get("/", response_model=List[schemas.Tapa])
def handle_read_tapas(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    tapas = crud.tapa.get_multi(db, skip=skip, limit=limit)
    # tapas = [tapa for tapa in tapas if tapa.activa==True]
    return tapas

@router.post("/", response_model=schemas.Tapa)
def handle_create_tapa_with_tarjeta(
    *,
    db: Session = Depends(deps.get_db),
    tapa_con_producto_in: schemas.TapaConProductoCreate,    
):
    tapa, fue_creada, error_msg = crud.tapa.create_with_producto_data(
        db = db, 
        tapa_con_producto_in = tapa_con_producto_in
    )

    if not fue_creada:
        raise HTTPException(status_code=404, detail=error_msg)
    
    return tapa
