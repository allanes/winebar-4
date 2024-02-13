from datetime import datetime
from typing import Any, Dict, Optional, List
from fastapi import HTTPException

from sqlalchemy.orm import Session

# from sql_app.core.security import get_password_hash, verify_password
from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.models import PersonalInterno, Rol
from sql_app.schemas.tarjetas_y_usuarios.personal_interno import PersonalInternoCreate, PersonalInternoUpdate


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


personal_interno = CRUDPersonalInterno(PersonalInterno)

    # def update(self, db: Session, *, db_obj: PersonalInterno, obj_in: PersonalInternoUpdate | Dict[str, Any]) -> PersonalInterno:
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
    #     tarjeta = db.query(PersonalInterno).filter(PersonalInterno.id == tarjeta_id).first()
    #     if tarjeta:
    #         tarjeta.entregada = True
    #         tarjeta.presente_en_salon = True
    #         db.commit()

    # def devolver_al_bar(self, db: Session, tarjeta_id: int) -> None:
    #     tarjeta = db.query(PersonalInterno).filter(PersonalInterno.id == tarjeta_id).first()
    #     if tarjeta:
    #         tarjeta.entregada = False
    #         tarjeta.presente_en_salon = False
    #         db.commit()
