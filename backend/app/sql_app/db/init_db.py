from sqlalchemy.orm import Session

from sql_app import crud, schemas
from sql_app.core.config import settings
from sql_app.db import base  # noqa: F401

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    print('Inicializando base de datos')
    user = crud.personal_interno.get_active(db, id=settings.FIRST_SUPERUSER)
    if not user:
        ## Crear la tarjeta
        tarjeta_admin_in = schemas.TarjetaCreate(
            raw_rfid=settings.FIRST_SUPERUSER,
            rol_nombre='ADMIN'
        )
        tarjeta_admin, fue_creada, msg = crud.tarjeta.create_or_reactivate(db=db, obj_in=tarjeta_admin_in)    
        if not fue_creada:
            print(msg)
            return
        
        ## Crear el PersonalInterno
        user_in = schemas.PersonalInternoCreate(
            id=settings.FIRST_SUPERUSER,
            nombre="Nombre",
            apellido="Apellido",
            # email=settings.FIRST_SUPERUSER,
            # password=settings.FIRST_SUPERUSER_PASSWORD,
            # is_superuser=True,
        )
        user, fue_creado, msg = crud.personal_interno.create_or_reactivate(db, obj_in=user_in)  # noqa: F841
        if not fue_creado:
            print(msg)
            return

        ## Entregar tarjeta a personal
        user, fue_entregada, msg = crud.personal_interno.entregar_tarjeta_a_personal(
            db=db,
            personal_id=user.id,
            tarjeta_id=tarjeta_admin.id
        )
        if not fue_creada:
            print(msg)
            return
        
        ## Configuracion inicial de montos
        montos_cfg = schemas.ConfiguracionCreate(
            monto_maximo_orden_def=100000,
            monto_maximo_pedido_def=40000
        )
        montos_in_db = crud.configuracion.create(db=db, obj_in=montos_cfg)
        print(f'Configuracion de montos creada.')
        print(f'    {montos_in_db}')

        print('Base de datos inicializada')
