import os
from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
import pdfkit

from sql_app import crud, schemas
from sql_app.api import deps
from sql_app.core.config import settings
from sql_app.schemas.serializers import datetime_formatter

router = APIRouter()

templates = Jinja2Templates(directory=settings.TEMPLATES_PATH)
orden_detallada_template_filename = 'orden_detallada.html'

@router.get("/by-rfid/{tarjeta_id}", response_model=schemas.OrdenCompraDetallada)
def handle_read_orden_by_client_rfid(
    tarjeta_id: int,
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)],
    db: Session = Depends(deps.get_db),
):
    deps.sync_consumos_dependency(
        db=db, 
        tarjeta_id=tarjeta_id, 
        abierto_por_id=current_user.id
    )
    orden_in_db = crud.orden.get_orden_abierta_by_rfid(
        db=db, tarjeta_id=tarjeta_id
    )
    if orden_in_db is None:
        raise HTTPException(status_code=404, detail="No se encontró una orden abierta para esta tarjeta")
    
    orden_detallada = crud.orden.convertir_a_orden_detallada(
        db=db, orden=orden_in_db
    )
    return orden_detallada

@router.get("/by-name/{client_name}", response_model=list[schemas.OrdenCompraDetallada])
def handle_read_orden_abierta_by_client_name(
    client_name: str,
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)],
    check_turno_abierto: Annotated[bool, Depends(deps.check_turno_abierto)],
    db: Session = Depends(deps.get_db),
):
    # deps.sync_consumos_dependency(
    #     db=db, 
    #     tarjeta_id=client_name, 
    #     abierto_por_id=current_user.id
    # )
    print(f'entrando a get_ordenes_abiertas_by_name...')
    ordenes_in_db = crud.orden.get_ordenes_abiertas_by_name(
        db=db, client_name=client_name
    )
    
    ordenes_detallada = [
        crud.orden.convertir_a_orden_detallada(db=db, orden=orden)
        for orden in ordenes_in_db
    ]
    return ordenes_detallada

@router.get("/by-turno/{turno_id}", response_model=List[schemas.OrdenCompraDetallada])
def handle_read_orden_by_turno_id(
    turno_id: int,
    db: Session = Depends(deps.get_db)
):
    ordenes_in_db = crud.orden.get_by_turno_id(
        db=db, turno_id=turno_id
    )

    ordenes_detalladas = [crud.orden.convertir_a_orden_detallada(
        db=db, orden=orden_in_db
    ) for orden_in_db in ordenes_in_db]
    
    return ordenes_detalladas

@router.post("/abrir", response_model=schemas.OrdenCompra)
def handle_abrir_orden(
    *,
    db: Session = Depends(deps.get_db),
    tarjeta_cliente: int,
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)],
    check_turno_abierto: Annotated[bool, Depends(deps.check_turno_abierto)],
):
    print(f'usuario logueado id: {current_user.id}')
    orden_in = schemas.OrdenCompraAbrir(
        abierta_por=current_user.id, 
        tarjeta_cliente=tarjeta_cliente
    )
    
    orden = crud.orden.abrir_orden(
        db = db, 
        abrir_orden_in = orden_in
    )

    if not orden:
        raise HTTPException(status_code=404, detail='No se pudo abrir el orden')
    
    return orden

@router.post("/cerrar", response_model=schemas.OrdenCompra)
def handle_cerrar_orden(
    *,
    id: int,
    db: Session = Depends(deps.get_db),
    info_pago: schemas.OrdenCompraInfoPago,
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)],
    check_turno_abierto: Annotated[bool, Depends(deps.check_turno_abierto)],
):
    print(f'usuario logueado id: {current_user.id}')
    
    orden, fue_cerrada, msg = crud.orden.cerrar_orden(
        db = db,
        id = id,
        cerrada_por_id = current_user.id,
        info_pago=info_pago
    )

    if not fue_cerrada:
        raise HTTPException(status_code=404, detail=msg)
    
    return orden

@router.get("/export/order/html", response_class=HTMLResponse)
async def export_order_to_html(
    id: int, 
    request: Request, 
    db: Session = Depends(deps.get_db),
):
    # current_user: schemas.PersonalInterno = kwargs.get('current_user', None)
    current_user = crud.personal_interno.get_multi(db=db, limit=1)[0]
    try:
        if not current_user:
            current_user = crud.personal_interno.get_multi(db=db, limit=1)[0]
        order_details = handle_read_orden_by_id(db=db, id=id, current_user=current_user)
        if order_details is not None:
            print(f'Orden recuperada. Procesando Plantilla')
            print(f'Directorio de plantillas: {os.path.abspath(settings.TEMPLATES_PATH)} (existe: {os.path.exists(settings.TEMPLATES_PATH)})')
        
        # Reverse the order of pedidos
        pedidos_reversed = []
        for idx in range(len(order_details.pedidos)):
            pedidos_reversed.append(order_details.pedidos[len(order_details.pedidos) - 1 - idx])
        order_details.pedidos = pedidos_reversed
        # Add the custom filter to Jinja2 environment
        templates.env.filters['format_datetime'] = datetime_formatter
        return templates.TemplateResponse(orden_detallada_template_filename, {"request": request, "order": order_details.model_dump()})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/order/pdf", response_class=FileResponse)
async def export_order_to_pdf(
    id: int, 
    request: Request, 
    db: Session = Depends(deps.get_db),
):
    # Define the directory for exported orders
    directory = settings.ORDENES_EXPORTADAS_PATH
    print(f'preparando para exportar orden en {directory=}')
    filename = f'{id}_detalles_orden.pdf'
    filepath = os.path.join(directory, filename)

    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Check if the file already exists
    if os.path.isfile(filepath):
        print(f'File {filename} already exists, returning existing file.')
        return FileResponse(path=filepath, filename=filename)

    try:
        # Get HTML content from the HTML endpoint
        response = await export_order_to_html(id=id, request=request, db=db)
        html_content = response.body.decode()

        print(f'Generating new PDF file: {filename}...')

        # Convert HTML to PDF using pdfkit
        pdfkit.from_string(input=html_content, output_path=filepath, verbose=True)

        print(f'PDF file {filename} created successfully.')

        # Return PDF file response
        return FileResponse(path=filepath, filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}", response_model=schemas.OrdenCompra)
def handle_update_orden(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    orden_in: schemas.OrdenCompraUpdate
):
    orden = crud.orden.get(db=db, id=id)
    if not orden:
        raise HTTPException(status_code=404, detail=f"Persona no encontrada con DNI {id}")
    
    orden = crud.orden.update(
        db=db, db_obj=orden, obj_in=orden_in
    )
    return orden

@router.get("/{id}", response_model=schemas.OrdenCompraDetallada)
def handle_read_orden_by_id(
    id: int,
    current_user: Annotated[schemas.PersonalInterno, Depends(deps.get_current_user)],
    db: Session = Depends(deps.get_db),
):
    orden_in_db = crud.orden.get(db=db, id=id)
    if orden_in_db is None:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    
    ## Reviso si esta abierta para sincronizar consumos de vino
    if not orden_in_db.cerrada_por:
        cliente_operando = crud.cliente_opera_con_tarjeta.get_by_cliente_id(db=db, cliente_id=orden_in_db.cliente_id)
        deps.sync_consumos_dependency(
            db=db, 
            tarjeta_id=cliente_operando.tarjeta_id, 
            abierto_por_id=current_user.id
        )
        orden_in_db = crud.orden.get(db=db, id=id)
    
    orden_detallada = crud.orden.convertir_a_orden_detallada(
        db=db,
        orden=orden_in_db
    )

    return orden_detallada

@router.get("/", response_model=List[schemas.OrdenCompraDetallada])
def handle_read_ordens(
    db: Session = Depends(deps.get_db),
    para_turno_abierto: bool | None = None,
    skip: int = 0,
    limit: int = 100,
    order_by: str = '',
    order_asc: bool = True
):
    if not para_turno_abierto:
        para_turno_abierto = False

    ordens = None
    if para_turno_abierto:
        print(f'Obteniendo ordenes para el turno abierto')
        turno_abierto = crud.turno.get_open_turno(db=db)
        if turno_abierto is not None:
            ordens = crud.orden.get_by_turno_id(db=db, turno_id=turno_abierto.id)
            print(f'    Turno abierto id: {turno_abierto.id}.')
            print(f'    Cant de ordenes recuperadas: {len(ordens)}.')
        else:
            print(f'    No se recuperó un turno abierto')
    
    if ordens is None:
        print(f'Obteniendo ordenes para todos los turnos')
        ordens = crud.orden.get_multi(db, skip=skip, limit=limit)
        print(f'    Cant de ordenes recuperadas: {len(ordens)}.')
    # ordens = [orden for orden in ordens if orden.activa==True]
    ordenes_detalladas = [crud.orden.convertir_a_orden_detallada(
        db=db, orden=orden_in_db
    ) for orden_in_db in ordens]
    
    return ordenes_detalladas