from typing import Annotated, Any
from datetime import timedelta

from fastapi import Depends, FastAPI, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm


from sql_app import crud, schemas, models
from sql_app.api import deps
from sql_app.core.config import settings
from sql_app.core import security
from sql_app.core.security import create_access_token

router = APIRouter()

@router.post("/access-token", response_model=schemas.Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(deps.get_db)],
    usar_api_key: bool = True
):
    user = crud.personal_interno.authenticate(
        db=db, 
        username=form_data.username, 
        password=form_data.password,
        usar_api_key=usar_api_key
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if usar_api_key:
        crud.personal_interno.post_authenticate_checks(
            db=db,
            username=form_data.username, 
            password=form_data.password,  
            user_in_db=user,      
        )
    
    delta_de_expiracion = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    if usar_api_key:
        delta_de_expiracion = settings.ACCESS_TOKEN_EXPIRE_MINUTES_LONG 
    print(f'Generando token válido por {delta_de_expiracion/60:.2f} hs.')
    access_token_expires = timedelta(minutes=delta_de_expiracion)
    access_token = create_access_token(
        data={"sub": str(user.tarjeta_id)}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


@router.get("/users/me", response_model=schemas.PersonalInterno)
async def read_users_me(
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)]
):
    return current_user

@router.post("/test-token", response_model=schemas.PersonalInterno)
def test_token(current_user: schemas.PersonalInterno = Depends(deps.get_current_user)):
    """
    Test access token
    """
    return current_user