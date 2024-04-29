import os
import sys
from typing import List
import tempfile

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session

from sql_app import crud, schemas
from sql_app.api import deps
from sql_app.core.config import settings
from sql_app.api.vitte_utils import vitte_api_client
import requests

router = APIRouter()

@router.get("/foto/{nombre}", response_class=FileResponse)
def handle_get_foto(
    *,
    nombre: str,
):
    url = vitte_api_client.retrieve_vino_img_url_by_nombre(nombre=nombre)
    if not url:
        raise HTTPException(status_code=404, detail=f"Imagen no encontrada para el vino con nombre {nombre}")
    print(f'url recuperado: {url}')
    # Use requests to fetch the image from the URL
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="No se pudo recuperar la imagen del vino.")

    # Save the image to a temporary file
    suffix = os.path.splitext(url)[1]  # Preserve the file extension
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name  # Get the path to the temp file

    return tmp_path

@router.get("/sync-menu-vinos")
def handle_sync_menu_vinos(db: Session = Depends(deps.get_db)):
    crud.vino.sync_products_with_vitte(db=db)
    return {}

@router.get("/sync-consumos-vinos-por-tarjeta")
def handle_sync_menu_vinos(db: Session = Depends(deps.get_db), raw_rfid: str = ''):
    crud.vino.sync_consumos_with_vitte_by_tarjeta(db=db, raw_tarjeta=raw_rfid)
    return {}