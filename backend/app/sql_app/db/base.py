# Import all the models, so that Base has them before being
# imported by Alembic
from sql_app.db.base_class import Base
from sql_app.models import (
    Rol,
    Tarjeta,
    # Cliente,
    # Personal_interno,
    # Detalles_adicionales,
    # Cliente_opera_con_tarjeta,
    # Personal_interno_opera_con_tarjeta
)
