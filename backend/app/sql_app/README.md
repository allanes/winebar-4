```mermaid
erDiagram
    Menu ||--o{ Producto : has
    Producto ||--|{ Tapa : has
    Producto ||--|{ Trago : has
    Producto ||--|{ Vino : has
    Producto ||--o{ ProductoPromocion : "participates in"
    Promocion ||--o{ ProductoPromocion : includes
    Turno ||--o{ OrdenCompra : manages
    OrdenCompra ||--o{ Pedido : includes
    Pedido ||--o{ Renglon : contains
    Renglon ||--|| Producto : "refers to"
    Rol ||--o{ Tarjeta : assigns
    Cliente ||--o{ DetallesAdicionales : "has"
    Cliente ||--o{ ClienteOperaConTarjeta : uses
    Tarjeta ||--o{ ClienteOperaConTarjeta : "linked to"
    PersonalInterno ||--o{ Tarjeta : "may have"
    Rol {
        id int
        nombre_corto string
        nombre_largo string
    }
    Tarjeta {
        id int
        raw_rfid string
        activa boolean
        fecha_alta datetime
        fecha_ultimo_uso datetime
        entregada boolean
        presente_en_salon boolean
        monto_precargado float
        rol_id int
    }
    Cliente {
        id int
        nombre string
        contrasena string
        activa boolean
    }
    PersonalInterno {
        id int
        usuario string
        nombre string
        contrasena string
        apellido string
        telefono string
        activa boolean
        tarjeta_id int
    }
    DetallesAdicionales {
        id int
        cliente_id int
        dni int
        apellido string
        email string
        telefono string
        domicilio string
    }
    ClienteOperaConTarjeta {
        id int
        id_cliente int
        tarjeta_id int
    }
    Menu {
        id int
        productos Producto[]
    }
    Producto {
        id int
        titulo string
        descripcion string
        precio float
        ultimo_cambio_precio datetime
        activa boolean
        stock int
        id_menu int
        tapa Tapa
        trago Trago
        vino Vino
    }
    Tapa {
        id int
        id_producto int
        foto string
    }
    Trago {
        id int
        id_producto int
        foto string
    }
    Vino {
        id int
        id_producto int
        id_vitte string
    }
    Promocion {
        id int
        descuento float
        vigencia_desde datetime
        vigencia_hasta datetime
        productos ProductoPromocion[]
    }
    ProductoPromocion {
        id int
        id_producto int
        id_promocion int
    }
    Turno {
        id int
        timestamp_apertura datetime
        timestamp_cierre datetime
        cantidad_de_ordenes int
        cantidad_tapas int
        cantidad_usuarios_vip int
        ingresos_totales float
        abierto_por int
        cerrado_por int
    }
    OrdenCompra {
        id int
        precarga_usada float
        monto_cobrado float
        monto_maximo_orden float
        timestamp_apertura_orden datetime
        timestamp_cierre_orden datetime
        turno_id int
        cliente_id int
        abierta_por int
        cerrada_por int
    }
    Pedido {
        id int
        timestamp_pedido datetime
        monto_maximo_pedido float
        orden_id int
        atendido_por int
        renglones Renglon[]
    }
    Renglon {
        id int
        cantidad int
        monto float
        promocion_aplicada boolean
        pedido_id int
        producto_id int
    }
    OrdenCompra }--|| Cliente : "belongs to"
    Cliente ||--o{ ClienteOperaConTarjeta : "operates with"
    Tarjeta ||--o{ ClienteOperaConTarjeta : "linked to"
    Producto ||--o{ Renglon : "included in"
    Pedido ||--o{ Renglon : "contains"
    OrdenCompra ||--o{ Pedido : "includes"
    Turno ||--o{ OrdenCompra : "manages"
    Menu ||--o{ Producto : "contains"
    Producto ||--|{ Tapa : "is a"
    Producto ||--|{ Trago : "is a"
    Producto ||--|{ Vino : "is a"
    Producto ||--o{ ProductoPromocion : "participates in"
    Promocion ||--o{ ProductoPromocion : "includes"
    Rol ||--o{ Tarjeta : "assigns"
    Cliente ||--o{ DetallesAdicionales : "has"
    PersonalInterno ||--o{ Tarjeta : "may have"
    Turno ||--|| PersonalInterno : "opened by"
    Turno ||--|| PersonalInterno : "closed by"
    OrdenCompra ||--|| PersonalInterno : "opened by"
    OrdenCompra ||--|| PersonalInterno : "closed by"
    Pedido ||--|| PersonalInterno : "attended by"
    Configuracion {
        id int
        monto_maximo_orden_def float
        monto_maximo_pedido_def float
        fecha_ultima_actualizacion datetime
        vitte_listado_nombres string
        vitte_listado_precios_sugeridos string
        vitte_listado_metadatos string
        vitte_ultima_sincronizacion datetime
    }
```
