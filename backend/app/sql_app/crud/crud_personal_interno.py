from datetime import datetime
from typing import Any, Dict, Optional, List
from fastapi import HTTPException

from sqlalchemy.orm import Session

# from sql_app.core.security import get_password_hash, verify_password
from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.models import PersonalInterno, Tarjeta
from sql_app.schemas.tarjetas_y_usuarios.personal_interno import PersonalInternoCreate, PersonalInternoUpdate

from sql_app.models import PersonalInternoOperaConTarjeta

class CRUDPersonalInterno(CRUDBaseWithActiveField[PersonalInterno, PersonalInternoCreate, PersonalInternoUpdate]):
    def get(self, db: Session, id: int) -> Optional[PersonalInterno]:
        return super().get_active(db=db, id=id)     

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[PersonalInterno]:
        return super().get_multi_active(db=db, skip=skip, limit=limit)
        
    def create(self, db: Session, *, obj_in: PersonalInternoCreate) -> PersonalInterno:
        # Campos adicionales y por defecto
        campo_id = obj_in.id
        campo_usuario = self.crear_nombre_usuario(usuario_in=obj_in)
        campo_nombre = obj_in.nombre
        campo_contraseña = self.hashear_contra(usuario_in=obj_in)
        campo_apellido = obj_in.apellido
        campo_telefono = obj_in.telefono
        campo_activo = True

        existing_personal = super().get_inactive(db=db, id=campo_id)
        if existing_personal:
            existing_personal.usuario = campo_usuario
            existing_personal.nombre = campo_nombre
            existing_personal.contraseña = campo_contraseña
            existing_personal.apellido = campo_apellido
            existing_personal.telefono = campo_telefono
            existing_personal.activo = campo_activo
            
            db_obj = existing_personal
        else:
            db_obj = PersonalInterno(
                id = campo_id,
                usuario = campo_usuario,
                nombre = campo_nombre,
                contraseña = campo_contraseña,
                apellido = campo_apellido,
                telefono = campo_telefono,
                activo = campo_activo,                
            )
            db.add(db_obj)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: int) -> PersonalInterno:
        return super().deactivate(db=db, id=id)
    
    def hashear_contra(self, usuario_in: PersonalInternoCreate) -> str:
        if not usuario_in.contra_sin_hash:
            contra_in = ''
        else:
            contra_in = usuario_in.contra_sin_hash

        return contra_in + str(usuario_in.id)
        
    def crear_nombre_usuario(self, usuario_in: PersonalInternoCreate) -> str:
        return usuario_in.id
    
    def asociar_con_tarjeta(self, db: Session, personal_id: int, tarjeta_id: int) -> bool:
        success = False
        

        # Create a new association if it doesn't exist
        new_association = PersonalInternoOperaConTarjeta(
            id_personal_interno=personal_id,
            tarjeta=tarjeta_id
        )
        db.add(new_association)

        # Retrieve the tarjeta and set entregada to true
        tarjeta = db.query(Tarjeta).filter(Tarjeta.id == tarjeta_id).first()
        if tarjeta:
            tarjeta.entregada = True
            success = True        
            db.commit()
            db.refresh(tarjeta)
        
        return success
    
    def check_puede_ser_creada(self, db: Session, personal_interno_in: PersonalInternoCreate) -> tuple[bool, str]:
        puede_crearse = True
        msg = ''
        
        preexiste_personal_interno = self.get(db=db, id=personal_interno_in.id)
        if preexiste_personal_interno:
            puede_crearse = False
            msg = f"Ya existe una persona con DNI {personal_interno_in.id}"    
        
        return puede_crearse, msg
    
    def check_puede_ser_borrada(self, db: Session, personal_interno_id: int) -> tuple[bool, str]:
        puede_borrarse = True
        msg = ''
        
        personal_interno = self.get(db=db, id=personal_interno_id)
        if not personal_interno:
            puede_borrarse = False
            msg=f"Persona no encontrada con DNI {personal_interno_id}"
        
        return puede_borrarse, msg
    
    def check_personal_puede_tener_nueva_tarjeta(self, db: Session, personal_interno_id: int, tarjeta_id: int) -> tuple[bool, str]:
        puede_borrarse = True
        msg = ''
        
        personal_interno_in_db = self.get(db=db, id=personal_interno_id)        
        if not personal_interno_in_db:
            puede_borrarse = False
            msg=f"Persona no encontrada con DNI {personal_interno_id}"

            return puede_borrarse, msg

        # Check if the association already exists
        existing_association = db.query(PersonalInternoOperaConTarjeta).filter(
            PersonalInternoOperaConTarjeta.id_personal_interno == personal_interno_id,
            PersonalInternoOperaConTarjeta.tarjeta == tarjeta_id
        )
        if existing_association:
            puede_borrarse = False
            msg=f"Esta persona ya tiene esa tarjeta asociada"

            return puede_borrarse, msg

        return puede_borrarse, msg

personal_interno = CRUDPersonalInterno(PersonalInterno)
