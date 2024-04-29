import os
from typing import Dict, Any, List
from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.models.inventario_y_promociones import Vino
from sql_app.schemas.inventario_y_promociones.vino import VinoCreate, VinoUpdate
from sql_app.schemas.inventario_y_promociones.producto import ProductoCreate, ProductoUpdate
from sql_app.api.vitte_utils import vitte_api_client
from sql_app.api.vitte_schemas import PicoDeModulo
from sql_app.crud.base import CRUDBase
from sql_app import crud

class CRUDVino(CRUDBase[Vino, VinoCreate, VinoUpdate]):
    def sync_products_with_vitte(self, db: Session):
        vinos_in_db = self.get_multi(db=db)        
        picos_con_vino = vitte_api_client.vitte_vinos_data_retriever.fetch_vino_ids_for_empresa()
        
        lista_interna_vinos_id_vitte = [int(vino.id_vitte) for vino in vinos_in_db]
        lista_tamaños = ['degustacion', 'media', 'copa']
        
        print(f'lista de vinos id en vitte antes de entrar al for: {lista_interna_vinos_id_vitte}')
        for pico in picos_con_vino:
            if pico.vino.id not in lista_interna_vinos_id_vitte:
                print(f'Creando vino con vitte_id {pico.id} ({pico.vino.nombre})')

                for tamaño_copa in lista_tamaños:
                    # Creo el producto: Recupero variables de interes 
                    nombre_campo_volumen = f'{tamaño_copa}Ml'
                    nombre_campo_precio = f'{tamaño_copa}Precio'
                    volumen = pico.model_dump().get(nombre_campo_volumen, '')
                    precio = pico.model_dump().get(nombre_campo_precio, 0)
                    
                    producto_in = ProductoCreate(
                        titulo=pico.vino.nombre,
                        descripcion=f'Volumen: {volumen} cc.',
                        precio=precio,
                        stock=0
                    )
                    # Creo el producto: creacion en db
                    producto_in_db, fue_creado, msg = crud.producto.create_or_reactivate(
                        db=db, obj_in=producto_in
                    )
                    if not fue_creado:
                        print(f'El vino id {pico.vinoId} ({pico.vino.nombre}) no se pudo crear en la tabla de productos')
                        # return None, fue_creado, msg
                    print(f'creado producto de vino en tabla productos. {producto_in_db.id}')
                    # Creo el vino
                    vino_in = VinoCreate(
                        volumen=volumen,
                        id_vitte=pico.vinoId,
                        id_producto=producto_in_db.id,
                    )

                    vino_in_db = self.create(db=db, obj_in=vino_in)

                    if vino_in_db is None:
                        msg = f'El vino id {pico.vinoId} ({pico.vino.nombre}) no se pudo crear'
                        print(msg)
                        # return None, False, msg
                    
                    lista_interna_vinos_id_vitte.append(pico.vino.id)
            else:
                # Comparo nombres
                vinos_in_db_por_vitte_id = [vino for vino in vinos_in_db if int(vino.id_vitte) == pico.vino.id]
                for vino_in_db_by_vitte in vinos_in_db_por_vitte_id:
                    if not vino_in_db_by_vitte.producto:
                        print(f'No se encontro un producto para el vino id {vino_in_db_by_vitte.id}')
                        continue

                    producto_actualizado = ProductoUpdate(
                        titulo=vino_in_db_by_vitte.producto.titulo,
                        descripcion=vino_in_db_by_vitte.producto.descripcion,
                        precio=vino_in_db_by_vitte.producto.precio,
                        stock=vino_in_db_by_vitte.producto.stock,
                    )
                    hubo_cambios = False
                    if vino_in_db_by_vitte.producto.titulo != pico.vino.nombre:
                        print(f'Nombres no coinciden')
                        print(f'    vino_vitte_id {vino_in_db_by_vitte.id_vitte}')
                        print(f'    nombre en db: {vino_in_db_by_vitte.producto.titulo}')
                        print(f'    nombre en vitte: {pico.vino.nombre}')    
                        
                        producto_actualizado.titulo = pico.vino.nombre
                        hubo_cambios = True
                        print('     Nombre actualizado')

                    if vino_in_db_by_vitte.volumen == pico.degustacionMl:
                        if vino_in_db_by_vitte.producto.precio != pico.degustacionPrecio:
                            print(f'Precio degustacion no coincide')
                            print(f'    vino_vitte_id {vino_in_db_by_vitte.id_vitte}')
                            print(f'    precio en db: {vino_in_db_by_vitte.producto.precio}')
                            print(f'    precio en vitte: {pico.degustacionPrecio}')    
                            
                            producto_actualizado.precio = pico.degustacionPrecio
                            hubo_cambios = True
                            print('     Precio degustacion actualizado')

                    elif vino_in_db_by_vitte.volumen == pico.mediaMl:
                        if vino_in_db_by_vitte.producto.precio != pico.mediaPrecio:
                            print(f'Precio Media no coincide')
                            print(f'    vino_vitte_id {vino_in_db_by_vitte.id_vitte}')
                            print(f'    precio en db: {vino_in_db_by_vitte.producto.precio}')
                            print(f'    precio en vitte: {pico.mediaPrecio}')    
                            
                            producto_actualizado.precio = pico.mediaPrecio
                            hubo_cambios = True
                            print('     Precio media actualizado')

                    elif vino_in_db_by_vitte.volumen == pico.copaMl:
                        if vino_in_db_by_vitte.producto.precio != pico.copaPrecio:
                            print(f'Precio Copa no coincide')
                            print(f'    vino_vitte_id {vino_in_db_by_vitte.id_vitte}')
                            print(f'    precio en db: {vino_in_db_by_vitte.producto.precio}')
                            print(f'    precio en vitte: {pico.copaPrecio}')    
                            
                            producto_actualizado.precio = pico.copaPrecio
                            hubo_cambios = True
                            print('     Precio copa actualizado')

                    if hubo_cambios:
                        crud.producto.update(
                            db=db,
                            db_obj=vino_in_db_by_vitte.producto,
                            obj_in=producto_actualizado
                        )                        
                    
        return 
        
    def remove(self, db: Session, *, id: int) -> Vino:
        vino_in_db = self.get(db=db, id=id)
        if vino_in_db is None: return None
        producto_id = vino_in_db.id_producto
        producto_removido, pudo_removerse, msg = crud.producto.deactivate(db=db, id=producto_id)
        vino_removida = super().remove(db, id=id)
        
        return vino_removida
    
    def update(self, db: Session, *, db_obj: Vino, obj_in: VinoUpdate | Dict[str, Any]) -> Vino:
        producto_actualizado_in_db = crud.producto.update(db=db, db_obj=db_obj.producto, obj_in=obj_in)
        
        db_obj.id_producto = producto_actualizado_in_db.id
        db.commit()
        db.refresh(db_obj)

        return db_obj
    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Vino]:
        return db.query(Vino).order_by(Vino.id).offset(skip).limit(limit).all()

    def get_by_product_id(self, db: Session, producto_id: int) -> Vino | None:
        vino_in_db = db.query(Vino)
        vino_in_db = vino_in_db.filter(Vino.id_producto == producto_id)
        vino_in_db = vino_in_db.first()
        return vino_in_db

vino = CRUDVino(Vino)