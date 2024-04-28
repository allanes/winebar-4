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
    VitteCategoriaField,
    ClienteVitteDesdeMaquina,
    TransaccionVino
)
from sql_app.core.config import settings
from sql_app.api.vitte_api_client import VitteApiClientBase


class VitteApiClient(VitteApiClientBase):
    def __init__(self):
        # Initialize the base class with any needed setup
        super().__init__()
        # self.reset_inactive_clients() 
        # self.mostrar_clientes()
    
    def listar_clientes_vitte(self, solo_activos=True) -> list[ClienteVitte]:
        self._ensure_authentication()
        self._fetch_empresa_id()
        print(f'VITTE EMPRESA ID {self.empresa_id}')
        headers = self._get_headers()
        url = f'{self.base_url}/cliente/searchCliente'
        payload = {
            'Apellido': None,
            'Nombre': None,
            'NumeroTarjeta': None,
            'VerActivos': solo_activos,
            'empresaId': self.empresa_id  # Accessing empresa_id directly which is already fetched
        }
        response = self.session.post(url, json=payload, headers=headers).json()
        clientes = [ClienteVitte(**data) for data in response.get('result', [])]


        print(f'Vitte: Listado de clientes recuperados. Cantidad: {len(response.get("result", []))}')
        # print(f'Vitte:      resp: {response}')
        print(f'Vitte:      success: {response.get("success")}')
        print(f'Vitte:      error: {response.get("error")}')
        return clientes

    def buscar_cliente_vitte_por_tarjeta_raw(self, tarjeta_id: str) -> Optional[ClienteVitteDesdeMaquina]:
        url = f"{self.base_url}/maquina/tarjeta/{tarjeta_id}/301/asdas"
        print(f"Vitte: Fetching client details for tarjeta ID: {tarjeta_id} from {url}")
        response = self.session.get(url, headers=self._get_headers()).json()
        
        if response and response['id'] == 0:  # Assuming 'id' == 0 signifies a null response indicating no such client exists
            print("Vitte:       No existing client found for the given tarjeta ID.")
            return None
        elif response and response['id'] != 0:
            ret = ClienteVitteDesdeMaquina(**response)
            print(f"Vitte:      Client found: {ret.model_dump()}")
            return ret
        else:
            print("Vitte:       Failed to retrieve valid client data or bad response from server.")
            return None
    
    def inhabilitar_cliente_vitte(self, data_cliente: schemas.ClienteOperaConTarjeta):
        print('Vitte: Pre-checking client in Vitte system')
        cliente_en_vitte = self.buscar_cliente_vitte_por_tarjeta_raw(tarjeta_id=data_cliente.tarjeta.raw_rfid)
        
        if cliente_en_vitte is None:
            print('Vitte:       Client not found in Vitte.')
            return False
        
        # Prepare the payload to update client as inactive
        cliente_a_cargar = self.prepare_cliente_payload(
            data_cliente_bar = data_cliente, 
            data_cliente_vitte = cliente_en_vitte, 
            inactivate=True
        )
        update_cliente_url = f'{self.base_url}/cliente/saveCliente'
        
        print('Vitte:       Updating client status to inactive...')
        response = self.session.post(url=update_cliente_url, json=cliente_a_cargar.dict(), headers=self._get_headers()).json()
        fue_exitoso = response.get('success', False)
        
        if not fue_exitoso:
            print('Vitte:       Failed to update client status.')
        
        pudo_borrar = self._borrar_cliente_vitte(cliente_id=cliente_en_vitte.id)
        
        return pudo_borrar

    def _borrar_cliente_vitte(self, cliente_id: int) -> bool:
        delete_url = f'{self.base_url}/cliente/{cliente_id}'
        print(f'Vitte: Deleting client ID: {cliente_id}...')
        response = self.session.delete(url=delete_url, headers=self._get_headers()).json()
        if response.get('success', False):
            print('Vitte:   Client deleted successfully.')
            return True
        else:
            print('Vitte:   Failed to delete client.')
            return False
    
    def cargar_saldo_cliente(self, cliente_id: int, monto_a_agregar: float) -> bool:
        print(f'Updating balance for client ID {cliente_id} by adding ${monto_a_agregar}')
        saldo_url = f'{self.base_url}/cliente/agregarSaldo'
        payload = {"clienteId": cliente_id, "saldo": monto_a_agregar}
        response = self.session.post(url=saldo_url, json=payload, headers=self._get_headers()).json()
        if response.get('success', False):
            print('Balance updated successfully.')
            return True
        else:
            print('Failed to update balance.')
            return False

    def cargar_o_actualizar_cliente_vitte(self, data_cliente: schemas.ClienteOperaConTarjeta):
        # Ensure all necessary properties are ready
        if not self.empresa_id or not self.client_id:
            self._fetch_initial_state()

        existing_cliente_vitte = self.buscar_cliente_vitte_por_tarjeta_raw(data_cliente.tarjeta.raw_rfid)
        if existing_cliente_vitte and existing_cliente_vitte.activo:
            print(f'Vitte: Client with ID {existing_cliente_vitte.id} already exists and is active. Please delete it first.')
            return False

        cliente_a_cargar = self.prepare_cliente_payload(data_cliente_bar=data_cliente, data_cliente_vitte=existing_cliente_vitte)
        save_cliente_url = f'{self.base_url}/cliente/saveCliente'
        print(f'Vitte: Creating or updating client...')
        response = self.session.post(url=save_cliente_url, json=cliente_a_cargar.dict(), headers=self._get_headers()).json()
        
        if response.get('success', False):
            print(f'Vitte:      Client operation successful. Details: {response.get("result")}')
            return True
        else:
            print('Vitte:       Failed to create or update client.')
            return False
        
    def prepare_cliente_payload(
        self, 
        data_cliente_bar: Optional[schemas.ClienteOperaConTarjeta], 
        data_cliente_vitte: Optional[ClienteVitteDesdeMaquina], 
        inactivate=False
    ) -> SaveClienteVitte:
        # payload = data_cliente_vitte.dict() if data_cliente_vitte else {}
        print(f'Vitte: preparando payload para postear cliente. {inactivate=}')
        if inactivate:
            payload = SaveClienteVitte(
                **data_cliente_vitte.model_dump(),
                tarjeta= '',
            )

            if not data_cliente_vitte.credenciales:
                credencial_a_guardar = VitteCredencialField(valor='')
            else:
                credencial_a_guardar = data_cliente_vitte.credenciales
                credencial_a_guardar.valor = ''
            
            payload.credencial = VitteCredencialField(valor='')
            payload.saldo = 0  # Optionally resetting the balance
        else:
            cred = VitteCredencialField(
                valor=data_cliente_bar.tarjeta.raw_rfid
            )
            print(f'Vitte: credencial creada para nuevo cliente (tipo {type(cred)}): {cred.model_dump()}')
            payload = SaveClienteVitte(
            # payload.update(
                id=data_cliente_vitte.id,
                activo=True,
                tarjeta=data_cliente_bar.tarjeta.raw_rfid,
                credencial=cred.model_dump(),
                saldo=10000,  # Default initial balance when creating a new client
                nombre=str(data_cliente_bar.cliente.id),
                apellido=data_cliente_bar.cliente.nombre,
                categoriaId=CategoriasVitte.CLIENTE.value,
                empresa='',
                empresaId=self.empresa_id
            )
        
        print(f'Vitte: Cliente preparado: {payload.model_dump()}')
        return payload

    def consultar_transacciones_vino_por_cliente(
        self, data_cliente: schemas.ClienteOperaConTarjeta
    ) -> list[TransaccionVino]:
        cliente_in_db = data_cliente.cliente
        print(f'data cliente: tipo: {type(data_cliente.cliente)}, valor: {data_cliente.cliente}')
        fechaDesde = (data_cliente.tarjeta.fecha_alta - dt.timedelta(days=1)).isoformat()[:10] + 'T03:00:00.000Z'
        fechaHasta = (datetime.now() + dt.timedelta(days=1)).isoformat()[:10] + 'T03:00:00.000Z'
        print(f'fecha desde: {fechaDesde}')
        print(f'fecha hasta: {fechaHasta}')
        query_params_fecha = {
            'fechaDesde': fechaDesde,
            'fechaHasta': fechaHasta
        }
        print(f'Vitte: Buscando transacciones desde {fechaDesde} hasta {fechaHasta}')

        consumos_url = 'https://app.vitte.com.ar/api/reporte/consumo'

        resp = self.session.post(url=consumos_url, json=query_params_fecha, headers=self._get_headers()).json()
        # print(f'Vitte: respuesta : {resp}')
        clave_buscada = str(data_cliente.cliente.id)

        transacciones = resp.get('result', [])
        transacciones = [TransaccionVino(**trans) for trans in transacciones]
        transacciones = [trans for trans in transacciones if trans.cliente == clave_buscada]

        print(f'Vitte:      transacciones encontradas: {len(transacciones)}')
        
        return transacciones
    
    def retrieve_vino_img_url_by_nombre(self, nombre: str) -> str:
        pass
        url = 'https://app.vitte.com.ar/api/maquina/estado/301/sfsdf'
        resp = self.session.get(url=url, headers=self._get_headers()).json()
        listado_modulos = resp.get('modulos', [])
        vino_id = None
        for modulo in listado_modulos:
            listado_picos = modulo.get('posiciones', [])
            for pico in listado_picos:
                if pico['vino']['nombre'] == nombre:
                    vino_id = pico['vino']['id']
                    print(f'Vitte: recuperado ID de vino: {vino_id}')
                    break
            if vino_id is not None:
                break

        if not vino_id:
            return ''
        
        return f'https://app.vitte.com.ar/api/Vino/Imagen/{vino_id}'

    def reset_inactive_clients(self):
        print('Vitte: Fetching all clients...')
        all_clients = self.listar_clientes_vitte(solo_activos=False)
        inactive_clients = [client for client in all_clients if not client.saldo]

        for cliente in inactive_clients:
            cliente_a_cargar = self.prepare_cliente_payload(
                data_cliente_vitte=cliente,
                inactivate=True
            )
            update_cliente_url = f'{self.base_url}/cliente/saveCliente'
        
            print('Vitte:       Updating client status to inactive...')
            response = self.session.post(url=update_cliente_url, json=cliente_a_cargar.dict(), headers=self._get_headers()).json()
            fue_exitoso = response.get('success', False)
            
            if not fue_exitoso:
                print('Vitte:       Failed to update client status.')

            self._borrar_cliente_vitte(cliente.id)
        
    def mostrar_clientes(self):
        clientes = self.listar_clientes_vitte(solo_activos=False)
        [print(cliente.model_dump()) for cliente in clientes]
            

vitte_api_client = VitteApiClient()