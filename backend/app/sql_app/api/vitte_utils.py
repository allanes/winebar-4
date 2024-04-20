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
    VitteCredencialField
)

login_dict = {
    'clave': "1234",
    'server': "Altacava",
    'usuario': "Altacava",
    'validate': "",
}
accept_str = 'application/json, text/plain, */*'
encoding_str = 'gzip, deflate, br'


@lru_cache
def obtener_token():
    login_url = 'https://app.vitte.com.ar/api/seguridad/login'
    resp = requests.post(url=login_url, json=login_dict).json()
    resp_exitosa = True  if 'success' in resp else False
    token_data = resp['result']['token']['token']
    usuario_data = resp['result']['usuario']
    return token_data, usuario_data

@lru_cache
def info_usuario_altacava():
    info_usuario_logueado_url = 'https://app.vitte.com.ar/api/local/localesUsuario/109'
    resp = requests.get(url=info_usuario_logueado_url).json()
    user_data = resp['result']
    return user_data[0]

def get_empresa_id() -> int:
    info = info_usuario_altacava()
    empresa_id = info['empresaId']
    return empresa_id

def obtener_headers():
    token = obtener_token()[0]
    print(f'token: {token}')
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': accept_str,
        'Accept-Enconding': encoding_str
    }
    return headers

def listar_clientes_vitte() -> list[ClienteVitte]:
    search_clientes_url = 'https://app.vitte.com.ar/api/cliente/search'
    filtro_empresa = {
        'Apellido': None,
        'Nombre': None,
        'NumeroTarjeta': None,
        'VerActivos': False,
        'empresaId': get_empresa_id()
    }
    # resp = requests.post(url=search_clientes_url, json=login_dict).json()
    resp = requests.post(url=search_clientes_url, json=filtro_empresa, headers=obtener_headers()).json()
    fue_exitoso = resp.get('success', False)

    if not fue_exitoso:
        return None
    
    resultados = resp.get('result', None)
    clientes_altacava = [ClienteVitte(**res) for res in resultados if res['empresaId'] == get_empresa_id()]

    return clientes_altacava

def buscar_cliente_vitte_por_tarjeta_raw(tarjeta_id: str) -> Optional[ClienteVitte]:
    clientes_altacava = listar_clientes_vitte()
    print(f'buscando cliente por tarjeta {tarjeta_id}')
    clientes_encontrados:list[ClienteVitte] = []
    for cliente_vitte in clientes_altacava:
        if cliente_vitte.nombre == tarjeta_id:
            clientes_encontrados.append(cliente_vitte)
            
    for cliente_encontrado in clientes_encontrados:
        if cliente_encontrado.activo == True:
            print(f'    cliente encontrado: {cliente_vitte}')
            return cliente_vitte
    
    # Si llegó acá, encontró clientes pero ninguno estaba ACTIVO
    if len(clientes_encontrados) > 0:
        return clientes_encontrados[0]
    
    return None

def borrar_cliente_vitte(data_cliente: schemas.ClienteOperaConTarjeta):
    print('Pre-chequeo de cliente en sistema Vitte')
    cliente_en_vitte = buscar_cliente_vitte_por_tarjeta_raw(tarjeta_id = data_cliente.tarjeta.raw_rfid)
    
    if cliente_en_vitte is None:
        print('No se encontró ese cliente en Vitte.')
        return None
    
    # if cliente_en_vitte.saldo > 0:
    #     print('El cliente todavia tiene saldo a cancelar.')
    #     return None

    # restablecer SALDO en CERO
    cargar_cliente_url = f'https://app.vitte.com.ar/api/cliente/{cliente_en_vitte.id}'
    print(f'haciendo req a {cargar_cliente_url}')
    resp = requests.delete(url=cargar_cliente_url, headers=obtener_headers()).json()
    fue_exitoso = resp.get('success', False)

    if not fue_exitoso:
        return False
    
    return True

def cargar_cliente_vitte(data_cliente: schemas.ClienteOperaConTarjeta):
    print('data del cliente')
    print(data_cliente)
    cliente_a_cargar = None
    SALDO_INICIAL = 10000
    
    print('Pre-chequeo de cliente en sistema Vitte')
    cliente_en_vitte = buscar_cliente_vitte_por_tarjeta_raw(tarjeta_id = data_cliente.tarjeta.raw_rfid)
    
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
        nombre=data_cliente.tarjeta.raw_rfid,
        apellido=data_cliente.cliente.nombre,
        categoriaId=CategoriasVitte.CLIENTE.value,
        empresa='',
        empresaId=get_empresa_id()
    )

    cliente_a_cargar = SaveClienteVitte(**payload)
    
    cargar_cliente_url = 'https://app.vitte.com.ar/api/cliente/saveCliente'

    print('No se encontro un cliente con esa tarjeta. Creando...')
    print(f'posteando json: {cliente_a_cargar.model_dump()}')
    resp = requests.post(url=cargar_cliente_url, json=cliente_a_cargar.model_dump(), headers=obtener_headers()).json()
    fue_exitoso = resp.get('success', False)

    if not fue_exitoso:
        return False
    
    resultados = resp.get('result', None)
    print(f'Cliente creado. Datos: {resultados}')

    return True

def cerrar_transacciones_vino(data_cliente: schemas.ClienteOperaConTarjeta) -> list:
    fechaDesde = (data_cliente.tarjeta.fecha_alta - dt.timedelta(days=1)).isoformat()[:10] + 'T03:00:00.000Z'
    fechaHasta = (datetime.now() + dt.timedelta(days=1)).isoformat()[:10] + 'T03:00:00.000Z'
    print(f'fecha desde: {fechaDesde}')
    print(f'fecha hasta: {fechaHasta}')
    query_params_fecha = {
        'fechaDesde': fechaDesde,
        'fechaHasta': fechaHasta
    }
    # query_params_fecha = {
    #     'fechaDesde': '2023-02-01T03:00:00.000Z',
    #     'fechaHasta': '2023-03-01T03:00:00.000Z'
    # }

    consumos_url = 'https://app.vitte.com.ar/api/reporte/consumo'

    resp = requests.post(url=consumos_url, json=query_params_fecha, headers=obtener_headers()).json()
    print(f'respuesta : {resp}')
    # clave_buscada = 'Martín'
    clave_buscada = str(data_cliente.tarjeta.raw_rfid)

    transacciones = []
    for trans_vino in resp.get('result', []):
        clave_extraida = trans_vino['cliente'].split(' ')[-1]
        print(f'clave extraida: {clave_extraida}, tipo: {type(clave_extraida)}')
        if clave_buscada==clave_extraida:
            transacciones.append(trans_vino)
            print(f'Transaccion encontrada: {clave_buscada}')

    # transacciones = [trans_vino for trans_vino in resp['result'] if clave_buscada==trans_vino['cliente'].split(' ')[-1]]
    
    return transacciones