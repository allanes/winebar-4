from typing import Type, List, Any
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sqlalchemy.inspection import inspect
from .base import CRUDBase, ModelType, CreateSchemaType, UpdateSchemaType


class CRUDBaseWithActiveField(CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        super().__init__(model)

    def get_active(self, db: Session, id: Any) -> ModelType:
        return db.query(self.model).filter(self.model.id == id, self.model.activa == True).first()
    
    def get_inactive(self, db: Session, id: Any) -> ModelType:
        return db.query(self.model).filter(self.model.id == id, self.model.activa == False).first()
    
    def get_multi_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).filter(self.active_field.activa == True).offset(skip).limit(limit).all()

    def deactivate(self, db: Session, *, id: int) -> ModelType:
        db_obj = db.query(self.model).get(id)
        db_obj.activa = False
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def activate(self, db: Session, *, id: int) -> ModelType:
        db_obj = db.query(self.model).get(id)
        db_obj.activa = True
        db.commit()
        db.refresh(db_obj)
        return db_obj
