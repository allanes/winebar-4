# test_crud_personal_interno.py

import pytest
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sql_app.api import deps
from sql_app.crud.crud_personal_interno import CRUDPersonalInterno
from sql_app.models.tarjetas_y_usuarios import PersonalInterno
from sql_app.schemas.tarjetas_y_usuarios.personal_interno import PersonalInternoCreate, PersonalInternoUpdate

# Fixture for DB session
@pytest.fixture
def db_session():
    """Fixture for creating a database session."""
    db_generator = deps.get_db()
    db_session = next(db_generator)  # Get the session object from the generator

    try:
        yield db_session
    finally:
        # Properly close the session and clean up
        next(db_generator, None)

# Session-scoped fixture for setup and teardown
@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_db():
    # Setup code here (if needed)
    
    yield  # Let tests run
    
    # Teardown: cleanup after all tests
    db_generator = deps.get_db()
    db_session = next(db_generator)
    try:
        # Delete the PersonalInterno record after all tests
        db_session.query(PersonalInterno).filter(PersonalInterno.id == 123).delete()
        db_session.commit()
    finally:
        next(db_generator, None)

# Test for creating a new PersonalInterno
def test_create_personal_interno(db_session: Session):
    personal_interno_in = PersonalInternoCreate(
        id=123, 
        nombre="Test", 
        apellido="User", 
        telefono="381",
        contra_sin_hash='contra')
    personal_interno, pudo_crearse, msg = CRUDPersonalInterno(PersonalInterno).create_or_reactivate(db=db_session, obj_in=personal_interno_in)
    assert pudo_crearse == True
    assert personal_interno.id == 123
    assert personal_interno.nombre == "Test"
    assert personal_interno.apellido == "User"
    assert personal_interno.telefono == "381"
    assert personal_interno.activa == True

# Test for reading an existing PersonalInterno by ID
def test_get_personal_interno(db_session: Session):
    personal_interno = CRUDPersonalInterno(PersonalInterno).get(db=db_session, id=123)
    assert personal_interno is not None
    assert personal_interno.id == 123

# Test for deactivating an existing PersonalInterno
def test_deactivate_personal_interno(db_session: Session):
    personal_interno, _, _ = CRUDPersonalInterno(PersonalInterno).deactivate(db=db_session, id=123)
    assert personal_interno is not None
    assert personal_interno.activa == False
    personal_interno_borrado = CRUDPersonalInterno(PersonalInterno).get_active(db=db_session, id=123)
    assert personal_interno_borrado is None

# Test for reactivating an existing PersonalInterno
def test_reactivate_personal_interno(db_session: Session):
    personal_interno_in = PersonalInternoCreate(
        id=123, 
        nombre="Reactivated", 
        apellido="User", 
        telefono="987654321",
        contra_sin_hash="nueva")
    personal_interno, _, _ = CRUDPersonalInterno(PersonalInterno).create_or_reactivate(db=db_session, obj_in=personal_interno_in)
    assert personal_interno.activa == True
    assert personal_interno.nombre == "Reactivated"
