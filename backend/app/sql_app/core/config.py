from pydantic import AnyHttpUrl, EmailStr, HttpUrl, validator
from pydantic_settings import SettingsConfigDict, BaseSettings
from typing import List, Optional, Union, Dict, Any
import bcrypt
import os
import secrets
from dotenv import load_dotenv

iniciado_desde_local = load_dotenv('..\..\..\.env')
# iniciado_desde_docker = os.path.exists('app') # otra forma de chequear
iniciado_desde_docker = not iniciado_desde_local
print(f'LOAD_DOTENV CARGADO: {iniciado_desde_local}')
print(f'INICIADO_DESDE_DOCKER: {iniciado_desde_docker}')
print(f'INICIADO_DESDE_LOCAL: {iniciado_desde_local}')
print(f'POSTGRES_SERVER: {os.getenv("POSTGRES_SERVER")}')
assert iniciado_desde_docker != iniciado_desde_local
print(os.path.abspath(os.path.curdir))

class Settings(BaseSettings):
    USE_BACKEND_PREFIX: bool = False if iniciado_desde_docker else True
    API_V1_STR: str = "/api/v1"
    FIRST_SUPERUSER: str
    API_KEY_TERMINAL_CAJA_1: str
    API_KEY_TERMINAL_TAPA_1: str
    API_KEY_TERMINAL_ADMIN: str
    SECRET_KEY: str = secrets.token_urlsafe(32)
    SALT: str = bcrypt.gensalt()
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ACCESS_TOKEN_EXPIRE_MINUTES_LONG: int
    ALGORITHM: str = "HS256"
    SERVER_NAME: str = "altacava-winebar-server"
    # SERVER_NAME: str = "localhost"
    # SERVER_HOST: AnyHttpUrl = "http://localhost"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    IMAGES_PATH: str = "default_images_path"
    ORDENES_EXPORTADAS_PATH: str = "default_ordenes_exportadas_path"
    TEMPLATES_PATH: str = "default_templates_path"

    # Vitte
    VITTE_SERVER: str
    VITTE_USUARIO: str
    VITTE_CLAVE: str

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
    POSTGRES_PORT: Optional[str] = '5432'
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    CONEXION: Optional[str] = None

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
    
    def __init__(self, **values):
        super().__init__(**values)
        if iniciado_desde_local:
            def transformar_a_local(ruta: str) -> str:
                ret = ruta.replace('/app/', '')
                ruta_aux = os.path.abspath('..')
                for carpeta in ret.split('/'):
                    ruta_aux = os.path.join(ruta_aux, carpeta)
                return ruta_aux

            self.IMAGES_PATH = transformar_a_local(self.IMAGES_PATH)
            self.ORDENES_EXPORTADAS_PATH = transformar_a_local(self.ORDENES_EXPORTADAS_PATH)
            self.TEMPLATES_PATH = transformar_a_local(self.TEMPLATES_PATH)
        
        self.CONEXION = self.assemble_db_string_to_show()

    def assemble_db_string_to_show(self):
        conexion = f'Servidor: {self.POSTGRES_SERVER}:{self.POSTGRES_PORT}, '
        conexion += f'db: {self.POSTGRES_DB}, '
        conexion += f'usuario: {self.POSTGRES_USER}'
        return conexion  
    
    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()

print(f'{settings.IMAGES_PATH=}')
print(f'{settings.ORDENES_EXPORTADAS_PATH=}')
print(f'{settings.TEMPLATES_PATH=}')
