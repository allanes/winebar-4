from sql_app.schemas import PersonalInternoCreate

def hashear_contra(usuario_in: PersonalInternoCreate) -> str:
    if not usuario_in.contra_sin_hash:
        contra_in = ''
    else:
        contra_in = usuario_in.contra_sin_hash

    return contra_in + str(usuario_in.id)

def obtener_pass_de_deactivacion() -> str:
    return 'generic_deactivation_password'
    
def crear_nombre_usuario(usuario_in: PersonalInternoCreate) -> str:
    return usuario_in.id