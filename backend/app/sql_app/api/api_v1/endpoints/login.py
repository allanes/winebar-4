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
    db: Annotated[Session, Depends(deps.get_db)]
):
    user = crud.personal_interno.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
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
def test_token(current_user: models.PersonalInterno = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user