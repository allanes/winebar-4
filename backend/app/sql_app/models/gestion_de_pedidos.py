from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from sql_app.db.base_class import Base  # Adjust import based on your setup

class Turno(Base):
    __tablename__ = 'turnos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp_apertura = Column(DateTime, nullable=False)
    timestamp_cierre = Column(DateTime, nullable=True)
    cantidad_de_ordenes = Column(Integer, nullable=False)
    cantidad_tapas = Column(Integer, nullable=False)
    cantidad_usuarios_vip = Column(Integer, nullable=False)
    monto_en_caja = Column(Float, nullable=False)
    comentarios = Column(Text, nullable=True)
    abierto_por = Column(Integer, ForeignKey('personal_interno.id'), nullable=False)
    cerrado_por = Column(Integer, ForeignKey('personal_interno.id'), nullable=True)

class OrdenCompra(Base):
    __tablename__ = 'ordenes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    precarga_usada = Column(Float, nullable=False)
    monto_cargado = Column(Float, nullable = False)
    monto_cobrado = Column(Float, nullable = False)
    monto_cobrado_efectivo = Column(Float, nullable = False)
    monto_cobrado_tarjeta = Column(Float, nullable = False)
    monto_cobrado_transferencia = Column(Float, nullable = False)
    monto_maximo_orden = Column(Float, nullable=False)
    monto_maximo_pedido = Column(Float, nullable=False)
    timestamp_apertura_orden = Column(DateTime, nullable=False)
    timestamp_cierre_orden = Column(DateTime, nullable=True)
    turno_id = Column(Integer, ForeignKey('turnos.id'))
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    abierta_por = Column(Integer, ForeignKey('personal_interno.id'))
    cerrada_por = Column(Integer, ForeignKey('personal_interno.id'), nullable=True)
    comentarios = Column(Text, nullable=True)
    turno = relationship("Turno")
    cliente = relationship("Cliente")

class Pedido(Base):
    __tablename__ = 'pedidos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp_pedido = Column(DateTime, nullable=True)
    cerrado = Column(Boolean, nullable=False)
    monto_maximo_pedido = Column(Float, nullable=False)
    monto_cargado = Column(Float, nullable=True)
    orden_id = Column(Integer, ForeignKey('ordenes.id'))
    atendido_por = Column(Integer, ForeignKey('personal_interno.id'))
    renglones = relationship("Renglon", back_populates="pedido", uselist=True)

class Renglon(Base):
    __tablename__ = 'renglones'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cantidad = Column(Integer, nullable=False)
    monto = Column(Float, nullable=False)
    promocion_aplicada = Column(Boolean, default=False)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'))
    producto_id = Column(Integer, ForeignKey('productos.id'))
    vitte_consumo_id = Column(Integer, nullable=True)
    pedido = relationship("Pedido", back_populates="renglones", uselist=False)
    producto = relationship("Producto")

class Configuracion(Base):
    __tablename__ = 'configuraciones'
    id = Column(Integer, primary_key=True, autoincrement=True)
    monto_maximo_orden_def = Column(Float, nullable=False)
    monto_maximo_pedido_def = Column(Float, nullable=False)
    fecha_ultima_actualizacion = Column(DateTime, nullable=False)

class LectorTapa(Base):
    __tablename__ = 'lectorestapas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_puerto = Column(String, nullable=False)
    nombre_terminal = Column(String, nullable=False)
    id_producto = Column(Integer, ForeignKey('productos.id'), nullable=True)
    producto = relationship("Producto")

