import datetime
# vitte_data_retriever.py
from sql_app.api.vitte_integration.vitte_api_client import VitteApiClientBase
from sql_app.api.vitte_integration.vitte_schemas import PicoDeModulo

class VitteWineDataRetriever(VitteApiClientBase):
    def __init__(self):
        super().__init__()

    def fetch_vino_ids_for_empresa(self) -> list[PicoDeModulo]:
        self._ensure_authentication()
        self._fetch_empresa_id()

        maquinas = self._fetch_maquinas_for_empresa()

        vinos_en_posicion = []
        retry = True
        retry_count = 0
        retry_max_attempts = 5
        while (retry == True):
            retry = False
            for maquina in maquinas:
                modulos = self._fetch_modulos_by_maquina(maquina['id'])
                for modulo in modulos:
                    posiciones = self._fetch_posiciones_by_modulo(modulo['id'])
                    for posicion in posiciones:
                        if posicion['vinoId'] is not None:
                            pico_response = self._fetch_posicion_by_id(posicion_id=posicion['id'])
                            pico_info = PicoDeModulo(**pico_response)
                            vinos_en_posicion.append(pico_info)
                            if pico_info.copaPrecio == 0 or pico_info.mediaPrecio == 0 or pico_info.degustacionPrecio == 0:
                                retry_count += 1
                                if retry_count == retry_max_attempts:
                                    file = open('error_de_precio.log', 'w')
                                    file.write(f'{pico_info=} \n {datetime.datetime.now()}')
                                    file.close()
                                    print(f'Existe un precio en 0 que no se puede actualizar:')
                                    print(f'    Maquina: {maquina}')
                                    print(f'    Modulo: {modulo}')
                                    print(f'    Posicion: {posicion}')
                                    retry = False
                                else:
                                    retry = True
        # print('Vinos en posicion:')
        # [print(vep) for vep in vinos_en_posicion]
        return vinos_en_posicion

    def _fetch_maquinas_for_empresa(self):
        url = f"{self.base_url}/maquina/searchByEmpresa/{self.local_id}"
        response = self._get_json(url, headers=self._get_headers())
        if response['success']:
            return response['result']
        else:
            print("Failed to fetch maquinas:", response.get("error"))
            return []

    def _fetch_modulos_by_maquina(self, maquina_id):
        url = f"{self.base_url}/modulo/byMaquina"
        payload = {"maquinaId": maquina_id}
        response = self._post_json(url, json=payload, headers=self._get_headers())
        if response['success']:
            return response['result']
        else:
            print("Failed to fetch modulos:", response.get("error"))
            return []

    def _fetch_posiciones_by_modulo(self, modulo_id):
        url = f"{self.base_url}/Posicion/byModulo"
        payload = {"ModuloId": modulo_id}
        response = self._post_json(url, json=payload, headers=self._get_headers())
        if response['success']:
            return response['result']
        else:
            print("Failed to fetch posiciones:", response.get("error"))
            return []
        
    def _fetch_posicion_by_id(self, posicion_id):
        url = f"{self.base_url}/Posicion/get/{posicion_id}"
        response = self._get_json(url, headers=self._get_headers())
        if response['success']:
            return response['result']
        else:
            print("Failed to fetch posicion (pico) by id:", response.get("error"))
            return []
