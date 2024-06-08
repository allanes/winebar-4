from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sql_app.core.config import settings

print(f'conectando a postgres. {settings.CONEXION}')
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
