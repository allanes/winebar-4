from typing import Annotated

from fastapi import Depends, FastAPI, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sql_app import crud, schemas
from sql_app.api import deps
from sql_app.core.security import hashear_contra
from sql_app.core.config import settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/token")

def fake_hash_password(password: str):
    return hashear_contra(password)

def fake_decode_token(token: str, db: Session) -> schemas.PersonalInterno:
    user = crud.personal_interno.get(db=db, id=int(token))
    return user

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(deps.get_db)]
):
    user = fake_decode_token(token, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no validas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    current_user: Annotated[schemas.PersonalInterno, Depends(get_current_user)]
):
    if not current_user.activa:
        raise HTTPException(status_code=400, detail="Personal Interno Inactivo")
    return current_user


@router.get("/prueba-login/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}

@router.get("/users/me")
async def read_users_me(current_user: Annotated[schemas.PersonalInterno, Depends(get_current_active_user)]):
    return current_user

@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(deps.get_db)]
):
    user = crud.personal_interno.get_active(db=db, id=form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Credenciales no válidas")
    # user = schemas.PersonalInternoInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.contraseña:
        raise HTTPException(status_code=400, detail="Credenciales no válidas")

    return {"access_token": user.id, "token_type": "bearer"}