from sql_app.schemas import PersonalInternoCreate, ClienteCreate

def hashear_contra(contra_in: str | None) -> str:
    if contra_in is None:
        contra_in = ''
    
    return contra_in * 3

def generar_pass_por_defecto(cliente_in: ClienteCreate) -> str:
    return cliente_in.nombre * 3

def obtener_pass_de_deactivacion() -> str:
    return 'generic_deactivation_password'
    
def crear_nombre_usuario(usuario_in: PersonalInternoCreate) -> str:
    return usuario_in.id