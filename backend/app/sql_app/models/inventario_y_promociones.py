from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from sql_app.db.base import Base  # Ensure this import matches your project structure

class Menu(Base):
    __tablename__ = 'menues'
    id = Column(Integer, primary_key=True, autoincrement=True)
    productos = relationship("Producto", back_populates="menu")

class Producto(Base):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    precio = Column(Float, nullable=False)
    ultimo_cambio_precio = Column(DateTime, nullable=False)
    activo = Column(Boolean, default=True)
    stock = Column(Integer, nullable=False)
    id_menu = Column(Integer, ForeignKey('menues.id'))
    menu = relationship("Menu", back_populates="productos")
    tapas = relationship("Tapa", back_populates="producto", uselist=False)
    tragos = relationship("Trago", back_populates="producto", uselist=False)
    vinos = relationship("Vino", back_populates="producto", uselist=False)

class Tapa(Base):
    __tablename__ = 'tapas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey('productos.id'))
    foto = Column(String, nullable=True)
    producto = relationship("Producto", back_populates="tapas")

class Trago(Base):
    __tablename__ = 'tragos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey('productos.id'))
    foto = Column(String, nullable=True)
    producto = relationship("Producto", back_populates="tragos")

class Vino(Base):
    __tablename__ = 'vinos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey('productos.id'))
    listado_nombres = Column(String, nullable=False)
    listado_precios_sugeridos = Column(String, nullable=False)
    listado_metadatos = Column(String, nullable=False)
    ultima_sincronizacion = Column(DateTime, nullable=False)
    producto = relationship("Producto", back_populates="vinos")

class Promocion(Base):
    __tablename__ = 'promociones'
    id = Column(Integer, primary_key=True, autoincrement=True)
    descuento = Column(Float, nullable=False)
    vigencia_desde = Column(DateTime, nullable=False)
    vigencia_hasta = Column(DateTime, nullable=False)
    productos = relationship("ProductoPromocion", back_populates="promocion")

class ProductoPromocion(Base):
    __tablename__ = 'productos_y_promociones'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey('productos.id'))
    id_promocion = Column(Integer, ForeignKey('promociones.id'))
    producto = relationship("Producto")
    promocion = relationship("Promocion", back_populates="productos")
