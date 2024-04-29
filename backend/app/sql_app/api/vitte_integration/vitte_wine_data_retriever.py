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
        for maquina in maquinas:
            modulos = self._fetch_modulos_by_maquina(maquina['id'])
            for modulo in modulos:
                posiciones = self._fetch_posiciones_by_modulo(modulo['id'])
                for posicion in posiciones:
                    if posicion['vinoId'] is not None:
                        pico_response = self._fetch_posicion_by_id(posicion_id=posicion['id'])
                        vinos_en_posicion.append(PicoDeModulo(**pico_response))

        return vinos_en_posicion

    def _fetch_maquinas_for_empresa(self):
        url = f"{self.base_url}/maquina/searchByEmpresa/{self.local_id}"
        response = self.session.get(url, headers=self._get_headers()).json()
        if response['success']:
            return response['result']
        else:
            print("Failed to fetch maquinas:", response.get("error"))
            return []

    def _fetch_modulos_by_maquina(self, maquina_id):
        url = f"{self.base_url}/modulo/byMaquina"
        payload = {"maquinaId": maquina_id}
        response = self.session.post(url, json=payload, headers=self._get_headers()).json()
        if response['success']:
            return response['result']
        else:
            print("Failed to fetch modulos:", response.get("error"))
            return []

    def _fetch_posiciones_by_modulo(self, modulo_id):
        url = f"{self.base_url}/Posicion/byModulo"
        payload = {"ModuloId": modulo_id}
        response = self.session.post(url, json=payload, headers=self._get_headers()).json()
        if response['success']:
            return response['result']
        else:
            print("Failed to fetch posiciones:", response.get("error"))
            return []
        
    def _fetch_posicion_by_id(self, posicion_id):
        url = f"{self.base_url}/Posicion/get/{posicion_id}"
        response = self.session.get(url, headers=self._get_headers()).json()
        if response['success']:
            return response['result']
        else:
            print("Failed to fetch posicion (pico) by id:", response.get("error"))
            return []
