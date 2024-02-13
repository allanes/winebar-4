from datetime import datetime
from typing import Any, Dict, Optional, List
from fastapi import HTTPException

from sqlalchemy.orm import Session

# from sql_app.core.security import get_password_hash, verify_password
from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.models import Tarjeta, Rol
from sql_app.schemas.tarjetas_y_usuarios.tarjeta import TarjetaCreate, TarjetaUpdate
from sql_app.schemas.validators import clean_tarjeta_id


class CRUDTarjeta(CRUDBaseWithActiveField[Tarjeta, TarjetaCreate, TarjetaUpdate]):
    def get(self, db: Session, id: int) -> Optional[Tarjeta]:
        return super().get_active(db=db, id=id)
    
    def get_by_raw_rfid(self, db: Session, raw_rfid: str) -> Optional[Tarjeta]:
        # Check if a Tarjeta has to be created or updated (based on 'activa')
        raw_rfid_transformado = clean_tarjeta_id(raw_rfid)
        return super().get_active(db=db, id=raw_rfid_transformado)        

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Tarjeta]:
        return super().get_multi_active(db=db, skip=skip, limit=limit)
        
    # def get_by_email(self, db: Session, *, email: str) -> Optional[Tarjeta]:
    #     return db.query(Tarjeta).filter(Tarjeta.email == email).first()

    def create(self, db: Session, *, obj_in: TarjetaCreate) -> Tarjeta:
        raw_rfid_transformado = clean_tarjeta_id(obj_in.raw_rfid)

        # Recupero el id del rol (asumiendo que ya existe)
        rol_en_db = db.query(Rol).filter(Rol.nombre_corto == obj_in.rol_nombre).first()        
        
        # Campos adicionales y por defecto
        campo_id = raw_rfid_transformado
        campo_raw_rfid = obj_in.raw_rfid
        campo_id_rol = rol_en_db.id
        campo_fecha_alta = datetime.utcnow()
        campo_presente_en_salon = False
        campo_entregada = False
        campo_activa = True
        campo_monto_precargado = -1

        existing_tarjeta = super().get_inactive(db=db, id=campo_id)
        if existing_tarjeta:
            existing_tarjeta.rol_id = campo_id_rol
            existing_tarjeta.raw_rfid = campo_raw_rfid
            existing_tarjeta.fecha_alta = campo_fecha_alta
            existing_tarjeta.presente_en_salon = campo_presente_en_salon
            existing_tarjeta.entregada = campo_entregada
            existing_tarjeta.activa = campo_activa
            existing_tarjeta.monto_precargado = campo_monto_precargado
            db_obj = existing_tarjeta
        else:
            db_obj = Tarjeta(
                id = campo_id,
                raw_rfid = campo_raw_rfid,
                rol_id = campo_id_rol,
                fecha_alta = campo_fecha_alta,
                fecha_ultimo_uso = None,
                presente_en_salon = campo_presente_en_salon,
                entregada = campo_entregada,
                activa = campo_activa,
                monto_precargado = campo_monto_precargado,
            )
            db.add(db_obj)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: int) -> Tarjeta:
        return super().deactivate(db=db, id=id)
    
tarjeta = CRUDTarjeta(Tarjeta)

    # def update(self, db: Session, *, db_obj: Tarjeta, obj_in: TarjetaUpdate | Dict[str, Any]) -> Tarjeta:
    #     if isinstance(obj_in, dict):
    #         update_data = obj_in
    #     else:
    #         update_data = obj_in.dict(exclude_unset=True)
        
    #     quiere_cambiar_presencia = update_data.get("presente_en_salon", None)
    #     no_esta_entregada = db_obj.entregada==False
    #     no_esta_para_entregar = update_data.get("entregada", None)
        
    #     if quiere_cambiar_presencia and (no_esta_entregada or no_esta_para_entregar): 
    #         raise HTTPException(status_code=404, detail=f"Para marcar la tarjeta como 'Presente en salón', primero debe entregarla.")

    #     # Set the current timestamp to fecha_ultimo_uso before updating
    #     update_data["fecha_ultimo_uso"] = datetime.utcnow()

    #     return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    # def check_puede_ser_asociada(self, db: Session, id_tarjeta: int) -> bool:
    #     tarjeta_in_db = self.get(db=db, id=id_tarjeta)
    #     if tarjeta_in_db is None:
    #         raise HTTPException(status_code=404, detail="La tarjeta leída no existe. Debe darla de alta antes de asociarla con alguien.")
    #     if tarjeta_in_db.entregada:
    #         raise HTTPException(status_code=404, detail="La tarjeta ya estaba entregada. El usuario debe devolverla primero")
    #     if tarjeta_in_db.presente_en_salon:
    #         raise HTTPException(status_code=404, detail="La tarjeta ya está siendo usada en el salón.")
        
    #     return True
    
    # def habilitar_cliente(self, db: Session, tarjeta_id: int) -> None:
    #     tarjeta = db.query(Tarjeta).filter(Tarjeta.id == tarjeta_id).first()
    #     if tarjeta:
    #         tarjeta.entregada = True
    #         tarjeta.presente_en_salon = True
    #         db.commit()

    # def devolver_al_bar(self, db: Session, tarjeta_id: int) -> None:
    #     tarjeta = db.query(Tarjeta).filter(Tarjeta.id == tarjeta_id).first()
    #     if tarjeta:
    #         tarjeta.entregada = False
    #         tarjeta.presente_en_salon = False
    #         db.commit()
