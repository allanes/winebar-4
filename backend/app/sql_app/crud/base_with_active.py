from typing import Type, List, Any
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sqlalchemy.inspection import inspect
from .base import CRUDBase, ModelType, CreateSchemaType, UpdateSchemaType


class CRUDBaseWithActiveField(CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        super().__init__(model)
        self.active_field = self.determine_active_field()

    def determine_active_field(self) -> str:
        model_columns = inspect(self.model).columns.keys()
        if "activo" in model_columns:
            return "activo"
        elif "activa" in model_columns:
            return "activa"
        else:
            raise ValueError("Active field not found in model")

    def get_active(self, db: Session, id: Any) -> ModelType:
        return db.query(self.model).filter(self.model.id == id, getattr(self.model, self.active_field) == True).first()
    
    def get_inactive(self, db: Session, id: Any) -> ModelType:
        return db.query(self.model).filter(self.model.id == id, getattr(self.model, self.active_field) == False).first()
    
    def get_multi_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).filter(getattr(self.model, self.active_field) == True).offset(skip).limit(limit).all()

    def deactivate(self, db: Session, *, id: int) -> ModelType:
        db_obj = db.query(self.model).get(id)
        setattr(db_obj, self.active_field, False)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def activate(self, db: Session, *, id: int) -> ModelType:
        db_obj = db.query(self.model).get(id)
        setattr(db_obj, self.active_field, True)
        db.commit()
        db.refresh(db_obj)
        return db_obj
