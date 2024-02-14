from datetime import datetime
from typing import Any, Dict, Optional, List
from fastapi import HTTPException

from sqlalchemy.orm import Session

# from sql_app.core.security import get_password_hash, verify_password
from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.models import PersonalInterno, Tarjeta
from sql_app.schemas.tarjetas_y_usuarios.personal_interno import PersonalInternoCreate, PersonalInternoUpdate

from . import crud_tarjeta

class CRUDPersonalInterno(CRUDBaseWithActiveField[PersonalInterno, PersonalInternoCreate, PersonalInternoUpdate]):
    def get(self, db: Session, id: int) -> Optional[PersonalInterno]:
        return super().get_active(db=db, id=id)     

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[PersonalInterno]:
        return super().get_multi_active(db=db, skip=skip, limit=limit)
        
    def create(self, db: Session, *, obj_in: PersonalInternoCreate) -> PersonalInterno:
        # Campos adicionales y por defecto
        personal_interno_defecto = PersonalInterno(
            id = obj_in.id,
            tarjeta_id = obj_in.tarjeta_id,
            usuario = self.crear_nombre_usuario(usuario_in=obj_in),
            nombre = obj_in.nombre,
            contraseña = self.hashear_contra(usuario_in=obj_in),
            apellido = obj_in.apellido,
            telefono = obj_in.telefono,
            activo = True,
        )

        existing_personal = super().get_inactive(db=db, id=personal_interno_defecto.id)
        if existing_personal:
            for campo, valor in personal_interno_defecto.__dict__.items():
                setattr(existing_personal, campo, valor)

            db_obj = existing_personal
        else:
            db_obj = personal_interno_defecto
            db.add(db_obj)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: int) -> PersonalInterno:
        db_obj = super().deactivate(db=db, id=id)
        db_obj.tarjeta_id = None
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def hashear_contra(self, usuario_in: PersonalInternoCreate) -> str:
        if not usuario_in.contra_sin_hash:
            contra_in = ''
        else:
            contra_in = usuario_in.contra_sin_hash

        return contra_in + str(usuario_in.id)
        
    def crear_nombre_usuario(self, usuario_in: PersonalInternoCreate) -> str:
        return usuario_in.id
    
    def entregar_tarjeta(self, db: Session, personal_id: int, tarjeta_id: int) -> bool:
        # Step 1: Clear any existing association with the tarjeta_id
        # This query retrieves all PersonalInterno records holding the tarjeta_id, excluding the current personal_id to prevent self-unlinking
        existing_associations = db.query(PersonalInterno).filter(PersonalInterno.tarjeta_id == tarjeta_id, PersonalInterno.id != personal_id).all()
        for personal in existing_associations:
            personal.tarjeta_id = None  # Clear the tarjeta_id for existing associations

        # Step 2: Retrieve the PersonalInterno instance to be updated
        personal_interno = db.query(PersonalInterno).filter(PersonalInterno.id == personal_id).first()
        if personal_interno:
            # Devuelvo tarjeta anterior
            tarjeta_vieja = personal_interno.tarjeta_id
            crud_tarjeta.tarjeta.devolver_a_banca(db=db, id=tarjeta_vieja)
            # Update the tarjeta_id field with new card
            personal_interno.tarjeta_id = tarjeta_id
            # Retrieve the tarjeta and set entregada to true
            tarjeta = db.query(Tarjeta).filter(Tarjeta.id == tarjeta_id).first()
            if tarjeta:
                tarjeta.entregada = True
                tarjeta.monto_precargado = 0
                # Commit the transaction to save changes
                db.commit()
                # Refresh the instances to reflect the updated state
                db.refresh(personal_interno)
                db.refresh(tarjeta)
        
        return personal_interno
    
    def devolver_tarjeta(self, db: Session, tarjeta_id: int) -> Tarjeta:
        # Step 1: Clear any existing association with the tarjeta_id
        existing_associations = db.query(PersonalInterno).filter(PersonalInterno.tarjeta_id == tarjeta_id).all()
        for personal in existing_associations:
            personal.tarjeta_id = None  # Clear the tarjeta_id for existing associations

        # Step 2: Retrieve the tarjeta and set entregada to false
        tarjeta_devuelta = crud_tarjeta.tarjeta.devolver_a_banca(db=db, id=tarjeta_id)
                
        return tarjeta_devuelta
    
    def check_puede_ser_creada(self, db: Session, personal_interno_in: PersonalInternoCreate) -> tuple[bool, str]:
        puede_crearse = True
        msg = ''
        
        preexiste_personal_interno = self.get(db=db, id=personal_interno_in.id)
        if preexiste_personal_interno:
            return False, f"Ya existe una persona con DNI {personal_interno_in.id}"

        tarjeta_nueva_id = personal_interno_in.tarjeta_id
        tarjeta_nueva_puede_usarse, msg_puede_usarse = crud_tarjeta.tarjeta.check_tarjeta_libre_para_asociar(db=db, id_tarjeta=tarjeta_nueva_id)
        if not tarjeta_nueva_puede_usarse:
            return False, msg_puede_usarse
        
        return puede_crearse, msg
    
    def check_puede_ser_borrada(self, db: Session, personal_interno_id: int) -> tuple[bool, str]:
        puede_borrarse = True
        msg = ''
        
        personal_interno = self.get(db=db, id=personal_interno_id)
        if not personal_interno:
            puede_borrarse = False
            msg=f"Persona no encontrada con DNI {personal_interno_id}"
        
        return puede_borrarse, msg
    
    def check_tarjeta_puede_ser_entregada(self, db: Session, personal_id: int, tarjeta_id: int) -> tuple[bool, str]:
        # Check if personal exists
        personal_interno = db.query(PersonalInterno).filter(PersonalInterno.id == personal_id).first()
        if not personal_interno:
            return False, f"Persona no encontrada con DNI {personal_id}"

        # Check if that personal has a previous tarjeta associated
        tarjeta_previa_id = personal_interno.tarjeta_id
        if tarjeta_previa_id:
            # If it does, call check_tarjeta_puede_ser_quitada_de_personal(). Continue if that returns true
            puede_quitarse, msg_quitarse = crud_tarjeta.tarjeta.check_tarjeta_puede_ser_quitada_de_personal(db=db, id_tarjeta=tarjeta_previa_id)
            if not puede_quitarse:
                return False, msg_quitarse
            # Continue if there wasn't a previous tarjeta or it can be disassociated
        # Continue directly if there wasn't a previous tarjeta
        
        # Check if the new tarjeta_id is free to be associated through its entregada field
        tarjeta_nueva_id = tarjeta_id
        tarjeta_nueva_puede_usarse, msg_puede_usarse = crud_tarjeta.tarjeta.check_tarjeta_libre_para_asociar(db=db, id_tarjeta=tarjeta_nueva_id)
        if not tarjeta_nueva_puede_usarse:
            return False, msg_puede_usarse
        
        # If all checks pass, the tarjeta can be associated
        return True, "La tarjeta puede ser entregada."

personal_interno = CRUDPersonalInterno(PersonalInterno)
