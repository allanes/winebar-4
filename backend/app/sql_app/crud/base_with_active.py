from typing import Optional, Type, List, Any
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sqlalchemy.inspection import inspect
from .base import CRUDBase, ModelType, CreateSchemaType, UpdateSchemaType


class CRUDBaseWithActiveField(CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        super().__init__(model)

    def get_active(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id, self.model.activa == True).first()
    
    def get_inactive(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id, self.model.activa == False).first()
    
    def get_multi_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).filter(self.active_field.activa == True).offset(skip).limit(limit).all()

    def deactivate(self, db: Session, id: int) -> tuple[Optional[ModelType], bool, str]:
        """Deactivate a record and apply deactivation defaults."""
        obj = self.get(db=db, id=id)
        if obj:
            check_passed, message = self.pre_deactivate_checks(obj)
            if not check_passed:
                return None, False, message
            
            self.apply_deactivation_defaults(obj)
            db.commit()
            db.refresh(obj)
            return obj, True, ""
    
    def create_or_reactivate(
            self, db: Session, *, obj_in: CreateSchemaType
        ) -> tuple[Optional[ModelType], bool, str]:
        existing_inactive = self.get_inactive(db=db, id=obj_in.id)
        
        if existing_inactive:
            check_passed, message = self.pre_update_checks(existing_inactive, obj_in)
            if not check_passed:
                return None, False, message  # Check failed, return with failure message
            
            self.apply_activation_defaults(existing_inactive)
            updated_obj = self.update(db=db, db_obj=existing_inactive, obj_in=obj_in)
            db.commit()
            return updated_obj, True, ""  # Successful update
        else:
            if not self.get_inactive(db=db, id=obj_in.id):
                check_passed, message = self.pre_create_checks(obj_in)
                if not check_passed:
                    return None, False, message
                
            created_obj = super().create(db=db, obj_in=obj_in)
            return created_obj, True, ""  # Successful creation

    def apply_deactivation_defaults(self, obj: ModelType) -> None:
        """Apply default values upon deactivation of a record."""
        # Generic implementation; specific models can override this
        obj.activa = False  # Reactivate the record
        

    def apply_activation_defaults(self, obj: ModelType) -> None:
        """Set default values upon reactivation of a record."""
        # Generic implementation; specific models can override this
        obj.activa = True  # Reactivate the record

    def pre_create_checks(self, obj_in: CreateSchemaType) -> tuple[bool, str]:
        """
        Perform specific logic checks before creating a new record.
        This method should be overridden in subclasses with specific validation logic.
        
        Returns:
        - A tuple of (bool, str), where bool indicates if the check passed, and str provides a failure message if any.
        """
        return True, ""  # Default implementation always passes. Override in subclasses.

    def pre_update_checks(self, db_obj: ModelType, obj_in: CreateSchemaType) -> tuple[bool, str]:
        """
        Perform specific logic checks before updating an existing record.
        This method should be overridden in subclasses with specific validation logic.
        
        Returns:
        - A tuple of (bool, str), where bool indicates if the check passed, and str provides a failure message if any.
        """
        return True, ""  # Default implementation always passes. Override in subclasses.

    def pre_deactivate_checks(self, db_obj: ModelType) -> tuple[bool, str]:
        """
        Perform specific logic checks before deactivating an existing record.
        This method should be overridden in subclasses with specific validation logic.

        Returns:
        - A tuple of (bool, str), where bool indicates if the check passed, and str provides a failure message if any.
        """
        return True, ""  # Default implementation always passes. Override in subclasses.
