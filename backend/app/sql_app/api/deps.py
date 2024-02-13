from typing import Generator

from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from sql_app import crud, models, schemas
# from sql_app.core import security
from sql_app.core.config import settings
from sql_app.db.session import SessionLocal


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

