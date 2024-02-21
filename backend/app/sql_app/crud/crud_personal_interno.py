from datetime import datetime
from typing import Any, Dict, Optional, List
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session

# from sql_app.core.security import get_password_hash, verify_password
from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.models import PersonalInterno, Tarjeta
from sql_app.schemas.tarjetas_y_usuarios.personal_interno import PersonalInternoCreate, PersonalInternoUpdate

from . import crud_tarjeta
from sql_app.core.security import hashear_contra, crear_nombre_usuario, obtener_pass_de_deactivacion

class CRUDPersonalInterno(CRUDBaseWithActiveField[PersonalInterno, PersonalInternoCreate, PersonalInternoUpdate]):
    ### Functions override section
    def apply_deactivation_defaults(self, obj: PersonalInterno, db: Session = None) -> None:
        obj.activa = False
        # super().apply_deactivation_defaults(personal_obj) # mismo que la linea de arriba
        obj.tarjeta_id = None
        obj.contraseña = obtener_pass_de_deactivacion()

    def apply_activation_defaults(
            self, 
            obj_in: PersonalInternoCreate | PersonalInternoUpdate, 
            db_obj: PersonalInterno, 
            db: Session = None
        ) -> PersonalInterno:
        # super().apply_activation_defaults(obj)
        db_obj.id = obj_in.id
        db_obj.usuario = crear_nombre_usuario(usuario_in=obj_in)
        db_obj.nombre = obj_in.nombre
        db_obj.contraseña = hashear_contra(usuario_in=obj_in)
        db_obj.apellido = obj_in.apellido
        db_obj.telefono = obj_in.telefono
        db_obj.activa = True # mismo que la linea de arriba
        db_obj.tarjeta_id = None
        return db_obj
            
    def pre_create_checks(self, obj_in: PersonalInternoCreate, db: Session = None) -> tuple[bool, str]:
        puede_crearse = True
        msg = ''
        
        preexiste_personal_interno_activo = self.get_active(db=db, id=obj_in.id)
        if preexiste_personal_interno_activo is not None:
            return False, f"Ya existe una persona con DNI {obj_in.id}"

        return puede_crearse, msg
        
    def pre_deactivate_checks(self, db_obj_id: int, db: Session = None) -> tuple[bool, str]:
        puede_borrarse = True
        msg = ''
        
        personal_interno = self.get_active(db=db, id=db_obj_id)
        if not personal_interno:
            puede_borrarse = False
            msg=f"Persona no encontrada con DNI {db_obj_id}"
        
        return puede_borrarse, msg
    ### End of Functions override section
    
    def entregar_tarjeta_a_personal(self, db: Session, personal_id: int, tarjeta_id: int) -> tuple[PersonalInterno | None, bool, str]:
        # Step 0: check
        tarjeta_puede_asociarse, msg = self.pre_entrega_checks(
            db=db, personal_id=personal_id, tarjeta_id=tarjeta_id
        )
        if not tarjeta_puede_asociarse:
            return None, False, msg
        
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
        
        return personal_interno, True, ''
    
    def pre_entrega_checks(self, db: Session, personal_id: int, tarjeta_id: int) -> tuple[bool, str]:
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
    
    def devolver_tarjeta_de_personal(self, db: Session, tarjeta_id: int) -> tuple[Tarjeta, bool, str]:
        # Step 1: Clear any existing association with the tarjeta_id
        existing_associations = db.query(PersonalInterno).filter(PersonalInterno.tarjeta_id == tarjeta_id).all()
        for personal in existing_associations:
            personal.tarjeta_id = None  # Clear the tarjeta_id for existing associations

        # Step 2: Retrieve the tarjeta and set entregada to false
        tarjeta_devuelta = crud_tarjeta.tarjeta.devolver_a_banca(db=db, id=tarjeta_id)
                
        return tarjeta_devuelta, True, ''

personal_interno = CRUDPersonalInterno(PersonalInterno)
