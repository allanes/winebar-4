from typing import Dict, Optional, Type, List, Any
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
        return db.query(self.model).filter(self.model.activa == True).offset(skip).limit(limit).all()
    
    def get_multi(
            self, db: Session, *, only_active:int = True, skip: int = 0, limit: int = 100
        ) -> List[ModelType]:
        if only_active:
            return self.get_multi_active(db=db, skip=skip, limit=limit)
        
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        # obj_in_data = jsonable_encoder(obj_in)
        # db_obj = self.model(**obj_in_data)  # type: ignore
        db_obj = self.model()
        db_obj = self.apply_activation_defaults(
            obj_in=obj_in, db_obj=db_obj, db=db
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType | Dict[str, Any]) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db_obj = self.apply_activation_defaults(
            obj_in=obj_in, db_obj=db_obj, db=db
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def deactivate(self, db: Session, id: int) -> tuple[Optional[ModelType], bool, str]:
        """Deactivate a record and apply deactivation defaults."""
        obj = self.get(db=db, id=id)
        if obj is None:
            return None, False, "Objeto no encontrado para deshabilitar"
        
        check_passed, message = self.pre_deactivate_checks(db_obj_id=obj.id, db=db)
        if not check_passed:
            return None, False, message
        
        self.apply_deactivation_defaults(obj=obj, db=db)
        db.commit()
        db.refresh(obj)
        return obj, True, ""
    
    def create_or_reactivate(
            self, db: Session, *, obj_in: CreateSchemaType, custom_id_field: str = 'id'
        ) -> tuple[Optional[ModelType], bool, str]:
        existing_inactive = self.get_inactive(db=db, id=getattr(obj_in, custom_id_field))
        
        if existing_inactive:
            # Have to reactivate
            check_passed, message = self.pre_reactivate_checks(
                db_obj=existing_inactive, 
                obj_in=obj_in
            )
            if not check_passed:
                return None, False, message  # Check failed, return with failure message
            
            updated_obj = self.update(db=db, db_obj=existing_inactive, obj_in=obj_in)
            return updated_obj, True, ""  # Successful update
        else:
            # Have to create
            check_passed, message = self.pre_create_checks(
                db=db,
                obj_in=obj_in
            )
            if not check_passed:
                return None, False, message
                
            created_obj = self.create(db=db, obj_in=obj_in)
            return created_obj, True, ""  # Successful creation

    def apply_deactivation_defaults(self, obj: ModelType, db: Session = None) -> None:
        """Apply default values upon deactivation of a record."""
        # Generic implementation; specific models can override this
        obj.activa = False  # Reactivate the record
        

    def apply_activation_defaults(self, obj_in: CreateSchemaType | UpdateSchemaType, db_obj: ModelType, db: Session = None) -> ModelType:
        """Set default values upon reactivation of a record."""
        # Generic implementation; specific models can override this
        db_obj.activa = True  # Reactivate the record
        return db_obj
    
    def pre_create_checks(self, obj_in: CreateSchemaType, db: Session = None) -> tuple[bool, str]:
        """
        Perform specific logic checks before creating a new record.
        This method should be overridden in subclasses with specific validation logic.
        
        Returns:
        - A tuple of (bool, str), where bool indicates if the check passed, and str provides a failure message if any.
        """
        return True, ""  # Default implementation always passes. Override in subclasses.

    def pre_reactivate_checks(self, db_obj: ModelType, obj_in: CreateSchemaType | UpdateSchemaType, db: Session = None) -> tuple[bool, str]:
        """
        Perform specific logic checks before updating an existing record.
        This method should be overridden in subclasses with specific validation logic.
        
        Returns:
        - A tuple of (bool, str), where bool indicates if the check passed, and str provides a failure message if any.
        """
        return True, ""  # Default implementation always passes. Override in subclasses.

    def pre_deactivate_checks(self, db_obj_id: int, db: Session = None) -> tuple[bool, str]:
        """
        Perform specific logic checks before deactivating an existing record.
        This method should be overridden in subclasses with specific validation logic.

        Returns:
        - A tuple of (bool, str), where bool indicates if the check passed, and str provides a failure message if any.
        """
        return True, ""  # Default implementation always passes. Override in subclasses.
