# backend/app/sql_app/lifespan_handlers.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.orm import Session
from alembic.config import Config
from alembic import command

from sql_app.db.session import SessionLocal
from sql_app.db.init_db import init_db
from sql_app import crud

def get_alembic_ini_path() -> str:
    # Determine the base directory and construct the path to alembic.ini
    if os.path.exists("/app"):
        # Docker environment
        alembic_ini_path = "/app/alembic.ini"
    else:
        # Local environment
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alembic_ini_path = os.path.join(base_dir, 'alembic.ini')
    
    print(f"alembic_ini_path={alembic_ini_path}")
    return alembic_ini_path

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load Alembic configuration
    alembic_ini_path = get_alembic_ini_path()
    
    # Change working directory to the directory containing alembic.ini
    current_working_directory = os.getcwd()
    new_working_directory = os.path.dirname(alembic_ini_path)
    os.chdir(new_working_directory)
    
    try:
        alembic_cfg = Config(alembic_ini_path)
        command.upgrade(alembic_cfg, "head")

        db: Session = SessionLocal()
        if should_initialize_db(db):
            init_db(db)
        yield
    finally:
        # Revert working directory
        os.chdir(current_working_directory)
        db.close()

def should_initialize_db(db: Session) -> bool:
    should = crud.personal_interno.get_multi(db, only_active=False)
    if not should:
        return True
    print('Salteando inicializacion de db. La base de datos ya se encuentra inicializada.')
    return False
