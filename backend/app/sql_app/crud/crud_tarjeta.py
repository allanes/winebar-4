from datetime import datetime
from typing import Any, Dict, Optional, List
from fastapi import HTTPException

from sqlalchemy.orm import Session

# from sql_app.core.security import get_password_hash, verify_password
from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.models import Tarjeta, Rol
from sql_app.schemas.tarjetas_y_usuarios.tarjeta import TarjetaCreate, TarjetaUpdate
from sql_app.schemas.validators import clean_tarjeta_id
from . import crud_rol


class CRUDTarjeta(CRUDBaseWithActiveField[Tarjeta, TarjetaCreate, TarjetaUpdate]):
    def get_by_raw_rfid(self, db: Session, raw_rfid: str) -> Optional[Tarjeta]:
        # Check if a Tarjeta has to be created or updated (based on 'activa')
        raw_rfid_transformado = clean_tarjeta_id(raw_rfid)
        return super().get_active(db=db, id=raw_rfid_transformado)        
        
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
    
    def devolver_a_banca(self, db: Session, id: int) -> Tarjeta:
        db_obj = self.get(db=db, id=id)
        db_obj.entregada = False
        db_obj.presente_en_salon = False
        db_obj.monto_precargado = -1

        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: int) -> Tarjeta:
        self.devolver_a_banca(db=db, id=id)
        tarjeta_desactivada = super().deactivate(db=db, id=id)
        return tarjeta_desactivada
    
    def check_puede_ser_borrada(self, db: Session, id_tarjeta: int) -> tuple[bool, str]:
        puede_borrarse = True
        msg = ''
        
        tarjeta_in_db = self.get(db=db, id=id_tarjeta)
        if not tarjeta:
            puede_borrarse = False
            msg = "Tarjeta no encontrada"
            return puede_borrarse, msg
        else:
            if tarjeta_in_db.entregada:
                puede_borrarse = False
                msg = "La tarjeta está entregada. Debe ser devuelta primero"
                return puede_borrarse, msg
            if tarjeta_in_db.presente_en_salon:
                puede_borrarse = False
                msg = "La tarjeta está siendo usada en el salón"
                return puede_borrarse, msg
        
        return puede_borrarse, msg
    
    def check_puede_ser_creada(self, db: Session, tarjeta_in: TarjetaCreate) -> tuple[bool, str]:
        puede_crearse = True
        msg = ''
        
        rol_en_db = crud_rol.rol.get_by_name(db=db, name=tarjeta_in.rol_nombre)
        if not rol_en_db:
            puede_crearse = False
            msg = f"Rol '{tarjeta_in.rol_nombre}' no encontrado"
        else:
            try:
                preexiste_tarjeta = self.get_by_raw_rfid(db=db, raw_rfid=tarjeta_in.raw_rfid)
                if preexiste_tarjeta:
                    puede_crearse = False
                    msg = f"La tarjeta ya existe"
            except ValueError:
                puede_crearse = False
                msg = f"Tarjeta inválida"
        
        return puede_crearse, msg
    
    def check_tarjeta_libre_para_asociar(self, db: Session, id_tarjeta: int) -> bool:
        puede_asociarse = True
        msg = ''

        tarjeta_in_db = self.get(db=db, id=id_tarjeta)
        if tarjeta_in_db is None:
            puede_asociarse = False
            msg = "La tarjeta leída no existe. Debe darla de alta antes de asociarla con alguien."
            return puede_asociarse, msg
        if tarjeta_in_db.entregada:
            puede_asociarse = False
            msg = "La tarjeta ya estaba entregada. El usuario debe devolverla primero"
            return puede_asociarse, msg
        if tarjeta_in_db.presente_en_salon:
            puede_asociarse = False
            msg = "La tarjeta ya está siendo usada en el salón."
            return puede_asociarse, msg
        
        return puede_asociarse, msg
    
    def check_tarjeta_puede_ser_quitada_de_personal(self, db: Session, id_tarjeta: int) -> tuple[bool, str]:
        tarjeta = self.get(db=db, id=id_tarjeta)
        if tarjeta is None:
            return False, "La tarjeta no existe."
        if not tarjeta.entregada:
            return False, "La tarjeta no está marcada como entregada, por lo tanto no puede ser quitada."
        return True, ""

tarjeta = CRUDTarjeta(Tarjeta)