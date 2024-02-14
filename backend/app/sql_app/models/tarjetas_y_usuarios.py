from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from sql_app.db.base_class import Base  # Adjust the import based on your setup

class Rol(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_corto = Column(String, unique=True, nullable=False)
    nombre_largo = Column(String, unique=True, nullable=False)
    tarjetas = relationship("Tarjeta", back_populates="rol")

class Tarjeta(Base):
    __tablename__ = 'tarjetas'
    id = Column(Integer, primary_key=True, autoincrement=False)
    raw_rfid = Column(String, nullable=False)
    activa = Column(Boolean, default=True)
    fecha_alta = Column(DateTime, default=datetime.utcnow)
    fecha_ultimo_uso = Column(DateTime, nullable=True)
    entregada = Column(Boolean, default=False)
    presente_en_salon = Column(Boolean, default=False)
    monto_precargado = Column(Float, nullable=True)
    rol_id = Column(Integer, ForeignKey('roles.id'))
    rol = relationship("Rol", back_populates="tarjetas")

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    contraseña = Column(String, nullable=False)
    activa = Column(Boolean, nullable=False)
    tarjeta = relationship("ClienteOperaConTarjeta", back_populates="cliente")
    detalles_adicionales = relationship("DetallesAdicionales", back_populates="cliente")

class PersonalInterno(Base):
    __tablename__ = 'personal_interno'
    id = Column(Integer, primary_key=True, autoincrement=False)
    usuario = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    contraseña = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    telefono = Column(String, nullable=True)
    activa = Column(Boolean, nullable=False)
    tarjeta_id = Column(Integer, ForeignKey('tarjetas.id'), nullable=True)
    tarjeta = relationship("Tarjeta")

class DetallesAdicionales(Base):
    __tablename__ = 'cliente_detalles_adicionales'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    dni = Column(Integer, nullable=True)
    apellido = Column(String, nullable=True)
    email = Column(String, nullable=True)
    teléfono = Column(String, nullable=True)
    domicilio = Column(String, nullable=True)
    cliente = relationship("Cliente", back_populates="detalles_adicionales")

class ClienteOperaConTarjeta(Base):
    __tablename__ = 'clientes_y_tarjetas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey('clientes.id'))
    tarjeta = Column(Integer, ForeignKey('tarjetas.id'))
    cliente = relationship("Cliente", back_populates="tarjeta")

