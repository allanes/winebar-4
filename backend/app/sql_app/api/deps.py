from typing import Generator, Annotated

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from sql_app import crud, models, schemas
# from sql_app.core import security
from sql_app.core.config import settings
from sql_app.db.session import SessionLocal


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> models.PersonalInterno | None:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.personal_interno.get_by_rfid(db=db, tarjeta_id=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def check_turno_abierto(
    db: Annotated[Session, Depends(get_db)]
) ->bool:
    turno_abierto = crud.turno.get_open_turno(db=db)
    if turno_abierto is None:
        raise HTTPException(status_code=404, detail='No hay un turno abierto')
    return True