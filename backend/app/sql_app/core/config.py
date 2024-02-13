import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, Field, validator
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    USE_BACKEND_PREFIX: bool = Field(default=True)
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str = "altacava-winebar-server"
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator('API_V1_STR', pre=True)
    def set_api_v1_str(cls, v, values):
        use_backend_prefix = values.get('USE_BACKEND_PREFIX')
        if use_backend_prefix == True:
            ret = "/backend" + v
            return ret
        else:
            return v

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        
        # postgres_url_server = values.get("POSTGRES_SERVER")
        postgres_url_server = "localhost"
        print(f'Conectando a postgres server: {postgres_url_server}...')

        conexion = PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            # host=values.get("POSTGRES_SERVER"),
            host=postgres_url_server,
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

        # print(f'Conexion: {conexion}')
        return conexion

    class Config:
        case_sensitive = True


settings = Settings()