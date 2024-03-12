from pydantic import AnyHttpUrl, EmailStr, HttpUrl, validator
from pydantic_settings import SettingsConfigDict, BaseSettings
from typing import List, Optional, Union, Dict, Any
import bcrypt
import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    USE_BACKEND_PREFIX: bool = True
    API_V1_STR: str = "/api/v1"
    API_KEY_TERMINAL_CAJA_1: str
    API_KEY_TERMINAL_TAPA_1: str
    SECRET_KEY: str = secrets.token_urlsafe(32)
    SALT: str = bcrypt.gensalt()
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ACCESS_TOKEN_EXPIRE_MINUTES_LONG: int
    ALGORITHM: str = "HS256"
    SERVER_NAME: str = "altacava-winebar-server"
    # SERVER_NAME: str = "localhost"
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator('API_V1_STR', pre=True)
    def set_api_v1_str(cls, v, values):
        use_backend_prefix = values.get('USE_BACKEND_PREFIX', True)
        if use_backend_prefix:
            return "/backend" + v
        return v

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]], values: Dict[str, Any]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith('['):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        username = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        server = values.get("POSTGRES_SERVER", "localhost")
        port = values.get('POSTGRES_PORT', '5432')
        db = values.get("POSTGRES_DB")
        return f"postgresql://{username}:{password}@{server}:{port}/{db}"
    
    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()
