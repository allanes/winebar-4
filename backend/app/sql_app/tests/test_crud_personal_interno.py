import pytest
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sql_app.crud.crud_personal_interno import CRUDPersonalInterno
from sql_app.models.tarjetas_y_usuarios import PersonalInterno
from sql_app.schemas.tarjetas_y_usuarios.personal_interno import PersonalInternoCreate, PersonalInternoUpdate

# Fixture for DB session
@pytest.fixture
def db_session():
    # Assuming there's a function to provide a test database session
    return get_test_db_session()

# Test for creating a new PersonalInterno
def test_create_personal_interno(db_session: Session):
    personal_interno_in = PersonalInternoCreate(id=123, nombre="Test", apellido="User", telefono="123456789")
    personal_interno = CRUDPersonalInterno(PersonalInterno).create(db=db_session, obj_in=personal_interno_in)
    assert personal_interno.id == 123
    assert personal_interno.nombre == "Test"
    assert personal_interno.apellido == "User"
    assert personal_interno.telefono == "123456789"
    assert personal_interno.activa == True

# Test for reading an existing PersonalInterno by ID
def test_get_personal_interno(db_session: Session):
    personal_interno = CRUDPersonalInterno(PersonalInterno).get(db=db_session, id=123)
    assert personal_interno is not None
    assert personal_interno.id == 123

# Test for updating an existing PersonalInterno
def test_update_personal_interno(db_session: Session):
    update_data = {"nombre": "Updated", "apellido": "UserUpdated"}
    personal_interno_in = PersonalInternoUpdate(**update_data)
    personal_interno = CRUDPersonalInterno(PersonalInterno).update(db=db_session, db_obj_id=123, obj_in=personal_interno_in)
    assert personal_interno.nombre == "Updated"
    assert personal_interno.apellido == "UserUpdated"

# Test for deactivating an existing PersonalInterno
def test_deactivate_personal_interno(db_session: Session):
    personal_interno, _, _ = CRUDPersonalInterno(PersonalInterno).deactivate(db=db_session, id=123)
    assert personal_interno is not None
    assert personal_interno.activa == False

# Test for reactivating an existing PersonalInterno
def test_reactivate_personal_interno(db_session: Session):
    personal_interno_in = PersonalInternoCreate(id=123, nombre="Reactivated", apellido="User", telefono="987654321")
    personal_interno, _, _ = CRUDPersonalInterno(PersonalInterno).create_or_reactivate(db=db_session, obj_in=personal_interno_in)
    assert personal_interno.activa == True
    assert personal_interno.nombre == "Reactivated"

# Test for deleting an existing PersonalInterno
def test_delete_personal_interno(db_session: Session):
    personal_interno, _, _ = CRUDPersonalInterno(PersonalInterno).deactivate(db=db_session, id=123)
    assert personal_interno is not None
    # Assuming there's a method to actually remove the record from the database, which is not usually recommended for CRUD operations.
