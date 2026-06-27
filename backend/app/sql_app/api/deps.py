from datetime import datetime
from typing import Generator, Annotated

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from sql_app import crud, models, schemas
# from sql_app.core import security
from sql_app.core.config import settings
from sql_app.db.session import SessionLocal
from sql_app.api.vitte_integration.vitte_db_sync import (
    sync_products_with_vitte,
    sync_consumos_with_vitte_by_tarjeta
)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No se pudo validar las credenciales",
    headers={"WWW-Authenticate": "Bearer"},
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")
print(f'Token URL for login: {oauth2_scheme.model.model_dump()["flows"]["password"]["tokenUrl"]}')

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_token_data_logueado(
    token: Annotated[str, Depends(oauth2_scheme)]
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        terminal_nombre: str = payload.get("terminal_nombre")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(
            username=username,
            terminal_nombre=terminal_nombre
        )
    except JWTError:
        raise credentials_exception
    
    return token_data

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> models.PersonalInterno | None:
    token_data: schemas.TokenData = get_token_data_logueado(token=token)
    user = crud.personal_interno.get_by_rfid(db=db, tarjeta_id=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_terminal_tapa_logueada(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> str | None:
    token_data: schemas.TokenData = get_token_data_logueado(token=token)
    await get_current_user(db=db, token=token)

    print(f'Terminal logueada: {token_data.terminal_nombre}')
    if not token_data.terminal_nombre or token_data.terminal_nombre.find('TAPA') < 0:
        raise credentials_exception
    
    return token_data.terminal_nombre

async def check_turno_abierto(
    db: Annotated[Session, Depends(get_db)]
) ->bool:
    turno_abierto = crud.turno.get_open_turno(db=db)
    if turno_abierto is None:
        raise HTTPException(status_code=404, detail='No hay un turno abierto')
    return True

def sync_products_dependency(db: Session = Depends(get_db)):
    return sync_products_with_vitte(db=db)

def sync_consumos_dependency(
    db: Annotated[Session, Depends(get_db)],
    tarjeta_id: int = None, 
    abierto_por_id: int = None
) -> bool:
    if tarjeta_id is None or abierto_por_id is None:
        raise ValueError("Tarjeta ID and Abierto Por ID are required for syncing consumptions.")
    
    print(f'DEBUG_MSG tarjeta {tarjeta_id}: sincronizando consumos desde sync_consumos {datetime.now()}')
    synced = sync_consumos_with_vitte_by_tarjeta(db, tarjeta_id, abierto_por_id)
    print(f'DEBUG_MSG tarjeta {tarjeta_id}: fin de sinc de consumos with vitte {datetime.now()}')
    return synced
