from typing import Annotated
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from sql_app import crud, schemas, models
from sql_app.api import deps
from sql_app.core.security import hashear_contra
from sql_app.core.config import settings
from passlib.context import CryptContext

# Create the context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(db: Session, username: str) -> models.PersonalInterno:
    return crud.personal_interno.get_by_rfid(db=db, tarjeta_id=username)

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.contraseña):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# def fake_decode_token(token: str, db: Session) -> schemas.PersonalInterno:
#     user = get_user(db=db, username=token)
#     # user = crud.personal_interno.get(db=db, id=int(token))
#     return user

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(deps.get_db)]
):
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
    user = get_user(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/token", response_model=schemas.Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(deps.get_db)]
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.tarjeta_id}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


@router.get("/users/me", response_model=schemas.PersonalInterno)
async def read_users_me(current_user: Annotated[schemas.PersonalInterno, Depends(get_current_user)]):
    return current_user

@router.get("/users/hashear-algo")
async def read_users_me():
    hashed = get_password_hash('123')
    print(hashed)
    return hashed
    