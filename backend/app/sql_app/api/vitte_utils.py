from functools import lru_cache
import json
import datetime as dt
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sql_app import crud, models, schemas
import requests
from sql_app.api.vitte_schemas import (
    ClienteVitte, 
    RespuestaConsumo, 
    SaveClienteVitte, 
    CategoriasVitte, 
    VitteCredencialField,
    VitteCategoriaField
)
from sql_app.core.config import settings
from sql_app.api.vitte_api_client import VitteApiClientBase


class VitteApiClient(VitteApiClientBase):
    def __init__(self, empresa_id=None):
        # Initialize the base class with any needed setup
        super().__init__(empresa_id)
        # self.reset_inactive_clients()

    def listar_clientes_vitte(self, solo_activos=True) -> list[ClienteVitte]:
        print('VITTE_CLIENT: Entering listar_clientes_vitte')
        # Ensure headers are ready and include up-to-date authentication tokens
        headers = self._get_headers()
        
        url = f'{self.base_url}/cliente/searchCliente'
        # url = f'{self.base_url}/cliente/search'
        filtro_empresa = {
            'Apellido': None,
            'Nombre': None,
            'NumeroTarjeta': None,
            'VerActivos': solo_activos,
            'empresaId': self.empresa_id  # Accessing empresa_id directly which is already fetched
        }
        response = self.session.post(url=url, json=filtro_empresa, headers=headers).json()
        success = response.get('success', False)

        if success:
            clientes = [ClienteVitte(**res) for res in response.get('result', [])]
            print(f'    clientes recuperados: {clientes}')
        else:
            print('    no se tuvo éxito en la consulta')
            clientes = []

        print(f'    número de clientes recuperados: {len(clientes)}')
        return clientes

    def buscar_cliente_vitte_por_tarjeta_raw(self, tarjeta_id: str) -> Optional[ClienteVitte]:
        clientes_altacava = self.listar_clientes_vitte()
        print(f'buscando cliente por tarjeta {tarjeta_id}')
        clientes_encontrados:list[ClienteVitte] = []
        for cliente_vitte in clientes_altacava:
            tiene_cred = cliente_vitte.credencial
            cred = cliente_vitte.credencial.valor if tiene_cred else None
            if tiene_cred and cred == tarjeta_id:
                clientes_encontrados.append(cliente_vitte)
                
        for cliente_encontrado in clientes_encontrados:
            if cliente_encontrado.activo == True:
                print(f'    cliente encontrado: {cliente_vitte}')
                return cliente_vitte
        
        # Si llegó acá, encontró clientes pero ninguno estaba ACTIVO
        # if len(clientes_encontrados) > 0:
        #     return clientes_encontrados[0]
        
        return None

    def borrar_cliente_vitte(self, data_cliente: schemas.ClienteOperaConTarjeta):
        print('Pre-chequeo de cliente en sistema Vitte')
        cliente_en_vitte = self.buscar_cliente_vitte_por_tarjeta_raw(tarjeta_id = data_cliente.tarjeta.raw_rfid)
        
        if cliente_en_vitte is None:
            print('No se encontró ese cliente en Vitte.')
            return None
        
        # if cliente_en_vitte.saldo > 0:
        #     print('El cliente todavia tiene saldo a cancelar.')
        #     return None

        # # restablecer SALDO en CERO
        # if cliente_en_vitte.saldo > 0:
        #     print(f'Client has balance to settle. Resetting to zero...')
        #     if not self.cargar_saldo_cliente(cliente_en_vitte.id, -cliente_en_vitte.saldo):
        #         print('Failed to reset balance.')
        #         return False
            
        # borrar credencial
        payload = cliente_en_vitte.model_dump()
        tarjeta_in = data_cliente.tarjeta.raw_rfid

        if cliente_en_vitte.credencial:
            credencial_a_guardar = cliente_en_vitte.credencial 
            credencial_a_guardar.valor = ''
        else:
            credencial_a_guardar = VitteCredencialField(valor='')

        payload.update(
            id=cliente_en_vitte.id,
            activo=True,
            tarjeta= '',
            credencial=credencial_a_guardar.model_dump(),
            saldo=0,
            nombre=str(data_cliente.cliente.id),
            apellido=data_cliente.cliente.nombre,
            categoriaId=cliente_en_vitte.categoria.id,
            categoria=cliente_en_vitte.categoria if cliente_en_vitte.categoria else VitteCategoriaField(
                id=cliente_en_vitte.categoriaId,
                nombre=CategoriasVitte.CLIENTE,
                activo=True
            ),
            empresa=cliente_en_vitte.empresa,
            empresaId=cliente_en_vitte.empresaId
        )

        cliente_a_cargar = SaveClienteVitte(**payload)
        
        cargar_cliente_url = 'https://app.vitte.com.ar/api/cliente/saveCliente'

        print('No se encontro un cliente con esa tarjeta. Creando...')
        print(f'posteando json: {cliente_a_cargar.model_dump()}')
        resp = self.session.post(url=cargar_cliente_url, json=cliente_a_cargar.model_dump(), headers=self._get_headers()).json()
        fue_exitoso = resp.get('success', False)

        # Borro el cliente 
        cargar_cliente_url = f'https://app.vitte.com.ar/api/cliente/{cliente_en_vitte.id}'
        print(f'haciendo req a {cargar_cliente_url}')
        resp = self.session.delete(url=cargar_cliente_url, headers=self._get_headers()).json()
        fue_exitoso = resp.get('success', False)

        if not fue_exitoso:
            return False
        
        return True
    
    def cargar_saldo_cliente(self, cliente_id: int, monto_a_agregar: float):
        print(f'Updating balance for client ID {cliente_id} (agregando ${monto_a_agregar})')
        cliente_url = f'https://app.vitte.com.ar/api/cliente/agregarSaldo'
        
        payload = {
            "clienteId": cliente_id,
            "saldo": monto_a_agregar,
        }
        response = self.session.post(url=cliente_url, json=payload, headers=self._get_headers()).json()
        if response.get('success', False):
            print('Balance updated successfully.')
            return True
        else:
            print('Failed to update balance.')
            return False

    def cargar_cliente_vitte(self, data_cliente: schemas.ClienteOperaConTarjeta):
        print('data del cliente')
        print(data_cliente)
        cliente_a_cargar = None
        SALDO_INICIAL = 10000
        
        print('Pre-chequeo de cliente en sistema Vitte')
        cliente_en_vitte = self.buscar_cliente_vitte_por_tarjeta_raw(tarjeta_id = data_cliente.tarjeta.raw_rfid)
        
        if cliente_en_vitte is not None:
            # print(f'DEBERIA RETORNAR FALSO')
            if cliente_en_vitte.activo == True:
                print('El cliente ya existe en Vitte, debe borralo primero.')
                return False
                
        payload = cliente_en_vitte.dict() if cliente_en_vitte else {}
        tarjeta_in = data_cliente.tarjeta.raw_rfid
        payload.update(
            id=0,
            activo=True,
            tarjeta= tarjeta_in,
            credencial= VitteCredencialField(valor=tarjeta_in),
            saldo=SALDO_INICIAL,
            nombre=str(data_cliente.cliente.id),
            apellido=data_cliente.cliente.nombre,
            categoriaId=CategoriasVitte.CLIENTE.value,
            empresa='',
            empresaId=self.empresa_id
        )

        cliente_a_cargar = SaveClienteVitte(**payload)
        
        cargar_cliente_url = 'https://app.vitte.com.ar/api/cliente/saveCliente'

        print('No se encontro un cliente con esa tarjeta. Creando...')
        print(f'posteando json: {cliente_a_cargar.model_dump()}')
        resp = self.session.post(url=cargar_cliente_url, json=cliente_a_cargar.model_dump(), headers=self._get_headers()).json()
        fue_exitoso = resp.get('success', False)

        if not fue_exitoso:
            return False
        
        resultados = resp.get('result', None)
        print(f'Cliente creado. Datos: {resultados}')

        return True

    def cerrar_transacciones_vino(self, data_cliente: schemas.ClienteOperaConTarjeta) -> list:
        fechaDesde = (data_cliente.tarjeta.fecha_alta - dt.timedelta(days=1)).isoformat()[:10] + 'T03:00:00.000Z'
        fechaHasta = (datetime.now() + dt.timedelta(days=1)).isoformat()[:10] + 'T03:00:00.000Z'
        print(f'fecha desde: {fechaDesde}')
        print(f'fecha hasta: {fechaHasta}')
        query_params_fecha = {
            'fechaDesde': fechaDesde,
            'fechaHasta': fechaHasta
        }

        consumos_url = 'https://app.vitte.com.ar/api/reporte/consumo'

        resp = self.session.post(url=consumos_url, json=query_params_fecha, headers=self._get_headers()).json()
        print(f'respuesta : {resp}')
        # clave_buscada = 'Martín'
        clave_buscada = str(data_cliente.cliente.id)

        transacciones = []
        for trans_vino in resp.get('result', []):
            clave_extraida = trans_vino['cliente'].split(' ')[0]
            print(f'clave extraida: {clave_extraida}, tipo: {type(clave_extraida)}')
            if clave_buscada==clave_extraida:
                transacciones.append(trans_vino)
                print(f'Transaccion encontrada: {clave_buscada}')

        # transacciones = [trans_vino for trans_vino in resp['result'] if clave_buscada==trans_vino['cliente'].split(' ')[-1]]
        
        return transacciones
    
    def reset_inactive_clients(self):
        print('Fetching all clients...')
        all_clients = self.listar_clientes_vitte()
        inactive_clients = [client for client in all_clients if not client.saldo]
        
        print(f'Found {len(inactive_clients)} inactive clients. Processing resets...')
        for client in inactive_clients:
            # # Nullifying tarjeta and credencial
            # reset_payload = SaveClienteVitte(
            #     id = client.id,
            #     activo=False,
            #     tarjeta= '',
            #     # credencial= VitteCredencialField(valor=tarjeta_in),
            #     saldo=0,
            #     nombre=client.nombre,
            #     apellido=client.apellido,
            #     categoriaId=client.categoriaId,
            #     categoria=client.categoria,
            #     empresa=client.empresa,
            #     empresaId=client.empresaId,
            #     # id = client.id,
            #     # activo = client.activo,
            #     # tarjeta = "",
            #     credencial = VitteCredencialField(valor=""),
            #     # saldo = 0,  # Resetting balance to zero
            #     # nombre = client.nombre,
            #     # apellido = client.apellido,
            #     # categoriaId = client.categoriaId,
            #     # empresaId = client.empresaId
            # )

            # # Assuming the endpoint to update the client supports a PATCH method
            # update_url = 'https://app.vitte.com.ar/api/cliente/saveCliente'
            # print(f'Resetting client ID {client.id}...')
            # response = self.session.post(url=update_url, json=reset_payload.model_dump(), headers=self._get_headers()).json()
            
            # Borro el cliente 
            cargar_cliente_url = f'https://app.vitte.com.ar/api/cliente/{client.id}'
            print(f'haciendo req a {cargar_cliente_url}')
            resp = self.session.delete(url=cargar_cliente_url, headers=self._get_headers()).json()
            fue_exitoso = resp.get('success', False)
            
            if fue_exitoso:
                print(f'Successfully reset client ID {client.id}.')
            else:
                print(f'Failed to reset client ID {client.id}. Response: {resp}')

            

vitte_api_client = VitteApiClient()