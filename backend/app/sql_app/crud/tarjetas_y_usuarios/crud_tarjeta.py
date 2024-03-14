from datetime import datetime
from typing import Any, Dict, Optional, List
from fastapi import HTTPException

from sqlalchemy.orm import Session

# from sql_app.core.security import get_password_hash, verify_password
from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.models import Tarjeta, Rol
from sql_app.schemas.tarjetas_y_usuarios.tarjeta import TarjetaCreate, TarjetaUpdate
# from sql_app.schemas.validators import clean_tarjeta_id
from . import crud_rol


class CRUDTarjeta(CRUDBaseWithActiveField[Tarjeta, TarjetaCreate, TarjetaUpdate]):
    ### Functions override section
    def get_multi(
            self, db: Session, *, only_active:int = True, skip: int = 0, limit: int = 100
        ) -> List[Tarjeta]:
        
        querry = db.query(self.model)
        if only_active:
            querry = querry.filter(self.model.activa == True)
        
        querry = querry.order_by(self.model.rol_id, self.model.id).offset(skip).limit(limit).all()
        return querry
    
    def apply_activation_defaults(
        self, 
        obj_in: TarjetaCreate | TarjetaUpdate, 
        db_obj: Tarjeta, 
        db: Session = None
    ) -> Tarjeta:
        # Recupero el id del rol (asumiendo que ya existe)
        rol_en_db = db.query(Rol).filter(Rol.nombre_corto == obj_in.rol_nombre).first()

        tarjeta_in = db_obj
        tarjeta_in.id = int(obj_in.raw_rfid),
        tarjeta_in.raw_rfid = obj_in.raw_rfid,
        tarjeta_in.rol_id = rol_en_db.id,
        tarjeta_in.fecha_alta = datetime.utcnow()
        tarjeta_in.fecha_ultimo_uso = None
        tarjeta_in.presente_en_salon = False
        tarjeta_in.entregada = False
        tarjeta_in.activa = True
        tarjeta_in.monto_precargado = 0
        return tarjeta_in
    
    def apply_deactivation_defaults(self, db_obj: Tarjeta, db: Session = None) -> None:
        
        tarjeta_in_db = db_obj
        tarjeta_in_db.fecha_alta = None
        tarjeta_in_db.fecha_ultimo_uso = None
        tarjeta_in_db.presente_en_salon = False
        tarjeta_in_db.entregada = False
        tarjeta_in_db.activa = False
        tarjeta_in_db.monto_precargado = -1

        db.commit()
        db.refresh(tarjeta_in_db)
    
    def pre_create_checks(self, obj_in: TarjetaCreate, db: Session = None) -> tuple[bool, str]:
        puede_crearse = True
        msg = ''
        tarjeta_in = obj_in
        
        ## Reviso si existe el rol
        rol_en_db = crud_rol.rol.get_by_name(db=db, name=tarjeta_in.rol_nombre)
        if not rol_en_db:
            msg = f"Rol '{tarjeta_in.rol_nombre}' no encontrado"
            return False, msg
        
        ## La busco entre las tarjetas activas. Si existe, retorna
        preexiste_tarjeta = None
        try:
            preexiste_tarjeta = super().get_active(db=db, id=int(obj_in.raw_rfid))
        except ValueError:
            msg = f"Tarjeta inválida"
            return False, msg
        
        if preexiste_tarjeta:
            msg = f"La tarjeta ya existe"
            return False, msg
        
        return puede_crearse, msg
    
    def pre_deactivate_checks(self, db_obj_id: int, db: Session = None) -> tuple[bool, str]:
        puede_borrarse = True
        msg = ''
        id_tarjeta = db_obj_id
        
        tarjeta_in_db = self.get(db=db, id=id_tarjeta)
        if not tarjeta:
            puede_borrarse = False
            msg = "Tarjeta no encontrada"
            return puede_borrarse, msg
        
        if tarjeta_in_db.entregada:
            puede_borrarse = False
            msg = "La tarjeta está entregada. Debe ser devuelta primero"
            return puede_borrarse, msg
        
        if tarjeta_in_db.presente_en_salon:
            puede_borrarse = False
            msg = "La tarjeta está siendo usada en el salón"
            return puede_borrarse, msg
        
        return puede_borrarse, msg
    
    def create_or_reactivate(self, db: Session, *, obj_in: TarjetaCreate) -> tuple[Tarjeta | None, bool, str]:
        return super().create_or_reactivate(db=db, obj_in=obj_in, custom_id_field='raw_rfid')
    ### End of Functions override section
        
    def devolver_a_banca(self, db: Session, id: int) -> Tarjeta:
        db_obj = self.get(db=db, id=id)
        db_obj.entregada = False
        db_obj.presente_en_salon = False
        db_obj.monto_precargado = -1

        db.commit()
        db.refresh(db_obj)
        return db_obj    
    
    def __check_tarjeta_libre_para_asociar(self, db: Session, id_tarjeta: int) -> tuple[bool, str]:
        puede_asociarse = True
        msg = ''

        tarjeta_in_db = self.get_active(db=db, id=id_tarjeta)
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
    
    def check_tarjeta_libre_para_asociar_cliente(self, db: Session, id_tarjeta: int) -> tuple[bool, str]:
        esta_libre, msg = self.__check_tarjeta_libre_para_asociar(db=db, id_tarjeta=id_tarjeta)
        if not esta_libre: return False, msg

        tarjeta_in_db = self.get_active(db=db, id=id_tarjeta)
        if tarjeta_in_db.rol.nombre_corto != 'CLIENTE_ESTANDAR':
            return False, 'La tarjeta debe ser de Cliente'
        
        return True, ''
    
    def check_tarjeta_libre_para_asociar_personal(self, db: Session, id_tarjeta: int) -> tuple[bool, str]:
        esta_libre, msg = self.__check_tarjeta_libre_para_asociar(db=db, id_tarjeta=id_tarjeta)
        if not esta_libre: return False, msg

        tarjeta_in_db = self.get_active(db=db, id=id_tarjeta)
        if tarjeta_in_db.rol.nombre_corto not in ['ADIMN', 'CAJERO', 'TAPERO']:
            return False, 'La tarjeta debe ser de un personal interno'
        
        return True, ''
    
    def check_tarjeta_puede_ser_quitada_de_personal(self, db: Session, id_tarjeta: int) -> tuple[bool, str]:
        tarjeta = self.get(db=db, id=id_tarjeta)
        if tarjeta is None:
            return False, "La tarjeta no existe."
        if not tarjeta.entregada:
            return False, "La tarjeta no está marcada como entregada, por lo tanto no puede ser quitada."
        return True, ""

tarjeta = CRUDTarjeta(Tarjeta)