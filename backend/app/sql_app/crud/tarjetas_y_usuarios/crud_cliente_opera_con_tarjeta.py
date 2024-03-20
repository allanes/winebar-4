from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from ..base import CRUDBase
from sql_app.models.tarjetas_y_usuarios import ClienteOperaConTarjeta
from sql_app.schemas.tarjetas_y_usuarios.cliente_opera_con_tarjeta import ClienteOperaConTarjetaCreate, ClienteOperaConTarjetaUpdate
from sql_app.schemas.tarjetas_y_usuarios.cliente import ClienteWithDetails
from sql_app.crud.tarjetas_y_usuarios import crud_detalles_adicionales 

class CRUDClienteOperaConTarjeta(CRUDBase[ClienteOperaConTarjeta, ClienteOperaConTarjetaCreate, ClienteOperaConTarjetaUpdate]):
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ClienteOperaConTarjeta]:
        return db.query(ClienteOperaConTarjeta).order_by(ClienteOperaConTarjeta.id.desc()).offset(skip).limit(limit).all()
    
    def get_by_cliente_id(self, db: Session, *, cliente_id: int) -> Optional[ClienteOperaConTarjeta]:
        return db.query(ClienteOperaConTarjeta).filter(ClienteOperaConTarjeta.id_cliente == cliente_id).first()

    def get_by_tarjeta_id(self, db: Session, *, tarjeta_id: int) -> Optional[ClienteOperaConTarjeta]:
        print(f'Buscando ClienteOperaConTarjeta con tarjeta {tarjeta_id}')
        db_obj = db.query(ClienteOperaConTarjeta).filter(ClienteOperaConTarjeta.tarjeta_id == tarjeta_id).order_by(ClienteOperaConTarjeta.tarjeta_id.desc()).first()
        # print(db_obj.__dict__)
        return db_obj
    
    def convertir_a_cliente_detallado(
        self, db: Session, clientes_a_convertir: list[ClienteOperaConTarjeta]
    ) -> list[ClienteWithDetails]:
        clientes_detallados = []
    
        for cliente_opera in clientes_a_convertir:
            detalle_adic = crud_detalles_adicionales.detalles_adicionales.get_by_cliente_id(
                db=db, cliente_id=cliente_opera.id_cliente
            )
            
            if detalle_adic is not None: 
                print(f'detalle adic recuperado: {detalle_adic}')
                print(f'detalle adic recuperado id: {detalle_adic.id}')
            clientes_detallados.append(ClienteWithDetails(
                **cliente_opera.cliente.__dict__,
                tarjeta=cliente_opera.tarjeta,
                detalle=detalle_adic.__dict__ if detalle_adic else None
            ))
    
        return clientes_detallados
        

cliente_opera_con_tarjeta = CRUDClienteOperaConTarjeta(ClienteOperaConTarjeta)
