from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from sql_app.db.base import Base  # Make sure to define your database connection and Base in a separate file

class Rol(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_corto = Column(String, unique=True, nullable=False)
    nombre_largo = Column(String, unique=True, nullable=False)
    tarjetas = relationship("Tarjeta", back_populates="rol")

class Tarjeta(Base):
    __tablename__ = 'tarjetas'
    id = Column(Integer, primary_key=True, unique=True)
    raw_rfid = Column(String, nullable=False)
    activa = Column(Boolean, default=True)
    fecha_alta = Column(DateTime, default=datetime.utcnow)
    fecha_ultimo_uso = Column(DateTime, nullable=True)
    entregada = Column(Boolean, default=False)
    presente_en_salon = Column(Boolean, default=False)
    monto_precargado = Column(Float, nullable=True)
    rol_id = Column(Integer, ForeignKey('roles.id'))
    rol = relationship("Rol", back_populates="tarjetas")

# class Cliente(Base):
#     __tablename__ = 'clientes'
#     ID_CLIENTE = Column(Integer, primary_key=True, autoincrement=True)
#     nombre = Column(String, nullable=False)
#     contraseña = Column(String, nullable=False)
#     detalles_adicionales = relationship("Detalles_adicionales", back_populates="cliente")
#     tarjetas = relationship("Cliente_opera_con_tarjeta", back_populates="cliente")

# class Personal_interno(Base):
#     __tablename__ = 'personal_interno'
#     DNI = Column(Integer, primary_key=True)
#     usuario = Column(String, nullable=False)
#     nombre = Column(String, nullable=False)
#     contraseña = Column(String, nullable=False)
#     apellido = Column(String, nullable=False)
#     telefono = Column(String, nullable=True)
#     tarjetas = relationship("Personal_interno_opera_con_tarjeta", back_populates="personal_interno")

# class Detalles_adicionales(Base):
#     __tablename__ = 'cliente_detalles_adicionales'
#     ID_DETALLE_ADICIONAL = Column(Integer, primary_key=True, autoincrement=True)
#     ID_CLIENTE = Column(Integer, ForeignKey('clientes.ID_CLIENTE'))
#     dni = Column(Integer, nullable=True)
#     apellido = Column(String, nullable=True)
#     email = Column(String, nullable=True)
#     teléfono = Column(String, nullable=True)
#     domicilio = Column(String, nullable=True)
#     cliente = relationship("Cliente", back_populates="detalles_adicionales")

# class Cliente_opera_con_tarjeta(Base):
#     __tablename__ = 'clientes_y_tarjetas'
#     ID_CLIENTE_OPERA_CON_TARJETA = Column(Integer, primary_key=True, autoincrement=True)
#     id_cliente = Column(Integer, ForeignKey('clientes.ID_CLIENTE'))
#     tarjeta = Column(Integer, ForeignKey('tarjetas.id'))
#     cliente = relationship("Cliente", back_populates="tarjetas")

# class Personal_interno_opera_con_tarjeta(Base):
#     __tablename__ = 'personal_interno_y_tarjetas'
#     ID_PERSONAL_INTERNO_OPERA_CON_TARJETA = Column(Integer, primary_key=True, autoincrement=True)
#     id_personal_interno = Column(Integer, ForeignKey('personal_interno.DNI'))
#     tarjeta = Column(Integer, ForeignKey('tarjetas.id'))
#     personal_interno = relationship("Personal_interno", back_populates="tarjetas")
