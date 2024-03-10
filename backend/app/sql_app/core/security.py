from datetime import datetime, timedelta, timezone
import bcrypt
from passlib.context import CryptContext
from jose import JWTError, jwt
from sql_app.schemas import PersonalInternoCreate, ClienteCreate
from sql_app.core.config import settings

# Create the context for password hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)

# Hash a password using bcrypt
def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=settings.SALT)
    hashed_password = hashed_password.decode('utf-8')
    return hashed_password

# Check if the provided password matches the stored password (hashed)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    verificada = bcrypt.checkpw(
        password = password_byte_enc , 
        hashed_password = hashed_password_byte_enc
    )
    return verificada

def hashear_contra(contra_in: str | None) -> str:
    if contra_in is None:
        contra_in = ''
    
    return contra_in * 3

def generar_pass_por_defecto(cliente_in: ClienteCreate) -> str:
    return cliente_in.nombre * 3

def obtener_pass_de_deactivacion() -> str:
    return 'generic_deactivation_password'
    
def crear_nombre_usuario(usuario_in: PersonalInternoCreate) -> str:
    return usuario_in.id