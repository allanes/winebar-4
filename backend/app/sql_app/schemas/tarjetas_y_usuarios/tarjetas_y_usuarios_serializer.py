
from sqlalchemy.orm import Session
from sql_app.api import deps
from sql_app.models.gestion_de_pedidos import OrdenCompra
from sql_app.schemas.tarjetas_y_usuarios.tarjeta import Tarjeta as TarjetaSchema

def serializer_para_tarjeta_operando(cliente_id: int, entregada: bool, presente_en_salon: bool) -> tuple[bool, bool]:
    db: Session = deps.get_db()
    db_session = next(db)

    orden_in_db = db_session.query(OrdenCompra)
    orden_in_db = orden_in_db.filter(OrdenCompra.cliente_id == cliente_id)
    orden_in_db = orden_in_db.first()
    
    if orden_in_db.cerrada_por:
        entregada = False
        presente_en_salon = False
    else:
        print(f'No se encontro una orden en clienteopera para cliente id {cliente_id} al serializar')

    return entregada, presente_en_salon

def serialize_tarjeta(cliente_id: int, tarjeta: TarjetaSchema) -> TarjetaSchema:
    if not tarjeta:
        return None
    
    entregada, presente_en_salon = serializer_para_tarjeta_operando(
        cliente_id = cliente_id,
        entregada = tarjeta.entregada,
        presente_en_salon = tarjeta.presente_en_salon,
    )
    tarjeta.entregada = entregada
    tarjeta.presente_en_salon = presente_en_salon
    return  tarjeta