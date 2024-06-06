import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from alembic.config import Config
from alembic import command

from sql_app.db.session import SessionLocal
from sql_app.db.init_db import init_db
from sql_app import crud

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_alembic_ini_path() -> str:
    # Determine the base directory and construct the path to alembic.ini
    if os.path.exists("/app"):
        # Docker environment
        alembic_ini_path = "/app/alembic.ini"
    else:
        # Local environment
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alembic_ini_path = os.path.join(base_dir, 'alembic.ini')
    
    logger.info(f"alembic_ini_path={alembic_ini_path}")
    return alembic_ini_path

async def wait_for_db():
    retries = 10
    while retries > 0:
        try:
            # Try to create a session to check if the DB is available
            db: Session = SessionLocal()
            db.execute(text('SELECT 1'))
            db.close()
            logger.info("Database is available.")
            return
        except OperationalError:
            logger.info("Database is not available yet, retrying...")
            retries -= 1
            await asyncio.sleep(5)
    raise Exception("Database is not available after multiple retries")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load Alembic configuration
    alembic_ini_path = get_alembic_ini_path()
    
    # Change working directory to the directory containing alembic.ini
    current_working_directory = os.getcwd()
    new_working_directory = os.path.dirname(alembic_ini_path)
    os.chdir(new_working_directory)
    
    db = None
    try:
        # Wait for the database to be available
        await wait_for_db()

        alembic_cfg = Config(alembic_ini_path)
        command.upgrade(alembic_cfg, "head")

        db = SessionLocal()
        if should_initialize_db(db):
            init_db(db)
        yield
    finally:
        # Revert working directory
        os.chdir(current_working_directory)
        if db:
            db.close()

def should_initialize_db(db: Session) -> bool:
    logger.info('Chequeando db...')
    should = crud.personal_interno.get_multi(db, only_active=False)
    if not should:
        logger.info('Necesita inicializar. Mandando Señal...')
        return True
    logger.info('Salteando inicializacion de db. La base de datos ya se encuentra inicializada.')
    return False
