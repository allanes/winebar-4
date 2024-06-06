import sys
import os
sys.path.append(os.path.abspath('..'))
    
# from sql_app.db.session import engine
# from sql_app.models import Rol, Tarjeta

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from sql_app.api.api_v1.api import api_router, tags_metadata
from sql_app.core.config import settings
from sql_app.lifespan_handlers import lifespan

load_dotenv()

app = FastAPI(
    title=settings.PROJECT_NAME, 
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    openapi_tags=tags_metadata,
    lifespan=lifespan
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

print(f'montando app en {settings.API_V1_STR}')
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == '__main__':
    uvicorn.run("main:app", port=5000, reload=True)