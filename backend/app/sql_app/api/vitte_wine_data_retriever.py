# vitte_data_retriever.py
from sql_app.api.vitte_api_client import VitteApiClientBase

class VitteWineDataRetriever(VitteApiClientBase):
    def __init__(self):
        super().__init__()

    def fetch_vino_ids_for_empresa(self):
        self._ensure_authentication()
        self._fetch_empresa_id()

        maquinas = self._fetch_maquinas_for_empresa()
        vino_ids = set()

        for maquina in maquinas:
            modulos = self._fetch_modulos_by_maquina(maquina['id'])
            for modulo in modulos:
                posiciones = self._fetch_posiciones_by_modulo(modulo['id'])
                for posicion in posiciones:
                    if posicion['vinoId'] is not None:
                        vino_ids.add(posicion['vinoId'])

        return list(vino_ids)

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
