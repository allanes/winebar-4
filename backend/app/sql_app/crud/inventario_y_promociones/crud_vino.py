import os
from typing import Dict, Any, List

from sqlalchemy.orm import Session
# from sql_app.crud.base_with_active import CRUDBaseWithActiveField
from sql_app.models.inventario_y_promociones import Vino, Producto as ProductoModel
from sql_app.models.gestion_de_pedidos import Renglon as RenglonModel
from sql_app.schemas.inventario_y_promociones.vino import VinoCreate, VinoUpdate
from sql_app.schemas.inventario_y_promociones.producto import ProductoCreate, ProductoUpdate
from sql_app.api.vitte_utils import vitte_api_client
from sql_app.api.vitte_schemas import PicoDeModulo
from sql_app.crud.base import CRUDBase
from sql_app import crud
from sql_app import schemas

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

                    producto_actualizar = ProductoUpdate(
                        titulo=vino_in_db_by_vitte.producto.titulo,
                        descripcion=vino_in_db_by_vitte.producto.descripcion,
                        precio=vino_in_db_by_vitte.producto.precio,
                        stock=vino_in_db_by_vitte.producto.stock,
                    )
                    hubo_cambios = False
                    volumen = 0
                    if vino_in_db_by_vitte.producto.titulo != pico.vino.nombre:
                        print(f'Nombres no coinciden')
                        print(f'    vino_vitte_id {vino_in_db_by_vitte.id_vitte}')
                        print(f'    nombre en db: {vino_in_db_by_vitte.producto.titulo}')
                        print(f'    nombre en vitte: {pico.vino.nombre}')    
                        
                        producto_actualizar.titulo = pico.vino.nombre
                        hubo_cambios = True
                        print('     Nombre actualizado')

                    if vino_in_db_by_vitte.volumen == pico.degustacionMl:
                        volumen = pico.degustacionMl
                        if vino_in_db_by_vitte.producto.precio != pico.degustacionPrecio:
                            print(f'Precio degustacion no coincide')
                            print(f'    vino_vitte_id {vino_in_db_by_vitte.id_vitte}')
                            print(f'    precio en db: {vino_in_db_by_vitte.producto.precio}')
                            print(f'    precio en vitte: {pico.degustacionPrecio}')    
                            
                            producto_actualizar.precio = pico.degustacionPrecio
                            hubo_cambios = True
                            print('     Precio degustacion actualizado')

                    elif vino_in_db_by_vitte.volumen == pico.mediaMl:
                        volumen = pico.mediaMl
                        if vino_in_db_by_vitte.producto.precio != pico.mediaPrecio:
                            print(f'Precio Media no coincide')
                            print(f'    vino_vitte_id {vino_in_db_by_vitte.id_vitte}')
                            print(f'    precio en db: {vino_in_db_by_vitte.producto.precio}')
                            print(f'    precio en vitte: {pico.mediaPrecio}')    
                            
                            producto_actualizar.precio = pico.mediaPrecio
                            hubo_cambios = True
                            print('     Precio media actualizado')

                    elif vino_in_db_by_vitte.volumen == pico.copaMl:
                        volumen = pico.copaMl
                        if vino_in_db_by_vitte.producto.precio != pico.copaPrecio:
                            print(f'Precio Copa no coincide')
                            print(f'    vino_vitte_id {vino_in_db_by_vitte.id_vitte}')
                            print(f'    precio en db: {vino_in_db_by_vitte.producto.precio}')
                            print(f'    precio en vitte: {pico.copaPrecio}')    
                            
                            producto_actualizar.precio = pico.copaPrecio
                            hubo_cambios = True
                            print('     Precio copa actualizado')

                    if hubo_cambios:
                        producto_actualizado = crud.producto.update(
                            db=db,
                            db_obj=vino_in_db_by_vitte.producto,
                            obj_in=producto_actualizar
                        )

                        vino_aux:Vino = db.query(Vino).get(vino_in_db_by_vitte.id)
                        vino_aux.id_producto = producto_actualizado.id
                        db.commit()
                        db.refresh(vino_aux)                        
                    
        return
    
    def sync_consumos_with_vitte_by_tarjeta(
        self, 
        db: Session, 
        raw_tarjeta: str, 
        abierto_por: schemas.PersonalInterno
    ):
        ## Recibiendo la tarjeta solo puedo valerme de una orden ABIERTA
        orden_del_cliente = crud.orden.get_orden_abierta_by_rfid(db=db, tarjeta_id=raw_tarjeta)
        if not orden_del_cliente:
            print(f'No se encontro un cliente activo con tarjeta {raw_tarjeta} para sincronizar los consumos con Vitte.')
            return
        
        consumos_vino = vitte_api_client.consultar_transacciones_vino_por_cliente(
            cliente_id=orden_del_cliente.cliente_id,
            fecha_alta_cliente=orden_del_cliente.timestamp_apertura_orden
        )
        
        [print(f'consumos recuperados: {consumo.model_dump()}') for consumo in consumos_vino]
        pedidos_guardados = crud.pedido.get_pedidos_por_tarjeta(db=db, tarjeta_id=raw_tarjeta)
        
        renglones_guardados = [RenglonModel]
        for ped in pedidos_guardados:
            renglones_guardados.extend(ped.renglones)
        consumos_vino_guardados = [reng.vitte_consumo_id for reng in renglones_guardados if reng.vitte_consumo_id is not None]
        print(f'Lista de consumos guardada: {consumos_vino_guardados}')
        for consumo in consumos_vino:
            if consumo.consumoId in consumos_vino_guardados:
                print(f'Consumo encontrado. Pasando al siguiente..')
                continue

            ## Abro pedido
            print(f'Llamando a abrir pedido...')
            pedido, pudo_abirse, msg = crud.pedido.abrir_pedido(
                db=db,
                pedido_in=schemas.PedidoCreate(atendido_por=abierto_por.id),
                tarjeta_cliente=raw_tarjeta
            )
            if not pudo_abirse:
                print(f'el consumo {consumo.vino} ({consumo.medida}) no se pudo cargar en la base de datos. error: {msg}')
                continue
            
            ## Agrego 1 renglon 
            print(f'Llamando a agregar producto...')
            vino_in_db = self.get_by_vitte_name(db=db, vitte_name=consumo.vino, tamaño_copa=consumo.volumen)
            if not vino_in_db:
                msg = f'No se encontro un producto en la db con el nombre {consumo.vino}'
                print(msg)
                return None, False, msg
            else:
                print(f'producto encontrado en db: {vino_in_db.__dict__}')

            renglon_creado, pudo_agregarse, msg = crud.pedido.agregar_producto_a_pedido(
                db=db,
                atendido_por=abierto_por.id,
                tarjeta_cliente=raw_tarjeta,
                renglon_in=schemas.RenglonCreate(
                    cantidad=1,
                    producto_id=vino_in_db.id_producto,
                    vitte_consumo_id=consumo.consumoId
                )
            )
            if not pudo_agregarse:
                print(f'el consumo {consumo.vino} ({consumo.medida}), producto id {vino_in_db.id} no se pudo cargar en la orden. error: {msg}')
                continue

            ## Cierro pedido
            print(f'Llamando a cerrar pedido...')
            crud.pedido.cerrar_pedido(
                db=db,
                cerrado_por=abierto_por.id,
                tarjeta_cliente=raw_tarjeta,   
                timestamp_cerrado=consumo.fecha
            )
        
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
    
    def get_by_vitte_name(self, db: Session, vitte_name: str, tamaño_copa: float) -> Vino | None:
        print(f'buscando vino por nombre y tam: {vitte_name}, {tamaño_copa}')
        productos_in_db = db.query(ProductoModel).filter(ProductoModel.titulo == vitte_name).all()

        if not productos_in_db:
            return None
        
        vinos_in_db = db.query(Vino).filter(Vino.id_producto.in_([producto.id for producto in productos_in_db]))
        vino_in_db = vinos_in_db.filter(Vino.volumen == tamaño_copa).first()

        return vino_in_db

vino = CRUDVino(Vino)