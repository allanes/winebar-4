# Cambios al Word por el feedback

## +1. Después de 2.4.2 — AGREGAR sección

> ### 2.4.3. Sostenibilidad de la integración
>
> El negocio fue concebido alrededor de las dispensadoras: al plantearse el proyecto con el cliente, este ya contaba con dos máquinas adquiridas. Se buscó y se consultó por una integración oficial del fabricante, ambos sin éxito. El reemplazo del firmware, considerado inicialmente, quedó fuera de esta etapa (sección 1.4.2). Por eso, y para no extender el alcance del proyecto o la inauguración del bar, es que se buscó el camino alternativo de hacer ingeniería inversa.
>
> De este camino, resultó que no se necesitaba replicar un gran número de operaciones para obtener las funcionalidades necesarias. Se usó la menor cantidad de operaciones posibles, listadas en la Tabla 2.1, y se encapsularon todas las llamadas en un solo módulo, para mantenibilidad del desarrollo. Tal módulo, además, valida cada respuesta contra el esquema conocido (sección 3.6.4). Como contingencia, las dispensadoras pueden operarse a mano desde el panel de Vitte.
>
> A largo plazo, si el fabricante discontinuara su nube, las máquinas seguirían siendo propiedad del cliente y podría reemplazarse el firmware y/o hardware que las controla por uno propio. El cliente asumió esta dependencia como un riesgo del negocio.

## +2. Tabla 2.6 — AGREGAR fila


| Id. | Riesgo                                                                    | Probabilidad | Impacto | Respuesta                                                                                                                             |
| --- | ------------------------------------------------------------------------- | ------------ | ------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| R9  | El fabricante discontinúa la nube de Vitte o impide el uso de su interfaz | Media        | Alto    | Riesgo aceptado por el cliente. Las máquinas son de su propiedad y puede reemplazarse el programa que las controla. Ver sección 2.4.3 |




## +3. Sección 3.1 — AGREGAR antes de "3.1.1. Actores"

> El recorrido típico de un cliente es el siguiente:
>
> 1. El cajero inicia sesión con su tarjeta y abre el turno de caja.
> 2. Al llegar un cliente, el cajero lo registra y le asigna una tarjeta. El sistema le abre una orden y habilita la tarjeta en las dispensadoras.
> 3. Durante su visita, el cliente se sirve vino con la tarjeta y pide tapas en el puesto de tapeo, sin pagar en cada consumo.
> 4. Al retirarse, devuelve la tarjeta en la caja. El sistema reúne sus consumos de vino y de tapas, el cajero cobra y cierra la orden.
> 5. Al terminar la jornada, el cajero cierra el turno e informa el dinero en caja.

Opcional: figura `figuras_v2/secuencia_general.png`. Si la usás, pasa a ser la Fig. 3.1 y hay que renumerar las demás del capítulo.

## 4. Sección 3.6.4, último párrafo — AGREGAR al final de la frase "…se rechazan de inmediato con un mensaje claro."

> En el caso particular de un cierre de orden cuando Vitte está fuera de línea, puede ser forzado si el cliente no puede esperar. Este y otros casos de manejo de errores se describen en la sección 3.6.7.



## +5. Después de 3.6.6 — AGREGAR sección

> ### 3.6.7. Consistencia de los datos y recuperación ante fallos
>
> Para garantizar la consistencia de datos en las integraciones con Vitte y Fudo, se emplearon mecanismos que funcionan en distintas capas del sistema. 
>
> Los consumos de vino son recuperados de Vitte y guardados localmente cada vez que una tarjeta Cliente es leída en la terminal de cajas o en la de tapas. Los consumos se recuperan siempre desde el momento (fecha y hora) que la tarjeta fue entregada al cliente, y se descartan los que ya existían (usando un identificador de consumo) para guardar sólo los nuevos. De esta forma, el sistema tiene siempre el consumo más reciente de vinos para cada tarjeta. Esto permite mantener los consumos actualizados mientras el cliente opera en el bar, y tolera las caídas de Vitte que pudieran haber ocurrido hasta que quiere pagar.
>
> Puede suceder que Vitte esté fuera de línea cuando se quiere dar de alta a un nuevo cliente. Este caso tiene una solución más simple desde lo práctico, si bien no desde lo técnico: se le puede pedir al cliente que vuelva a acercarse al mostrador en unos minutos. Esto es posible ya que el bar cuenta con mozos y una variedad de vinos bastante más amplia que la que soportan las máquinas solamente. Un cliente siempre puede hacer su pedido a un mozo, si no quisiera usar una tarjeta.

> En la situación de un cliente retirándose, se debe considerar la caída de ambos servicios, Vitte y Fudo. Si Vitte está fuera de línea cuando el cajero desea cobrar una tarjeta, se refleja tal información inmediatamente. Si no es posible que el cliente espere algunos minutos, la app ofrece el camino alternativo de forzar el cobro con los consumos hasta la última actualización local existente. Queda a criterio del cajero. La orden queda identificada como cerrada sin conexión, y el sistema queda reintentando periódicamente dar de baja la tarjeta en Vitte hasta que se concrete. Cuando sucede, además, deja asentados en la orden los consumos de vino que no se llegaron a cobrar.
>
> Por otro lado, con Fudo fuera de línea, el cajero puede optar por otra de las formas de pago permitidas (por ejemplo *Efectivo*), y luego cargar ese consumo manualmente desde la app de Fudo. La carga de consumos en Fudo ya ocurre para todos los pedidos a través de los mozos, por lo que es un proceso ya familiar para el personal.
>
> Por último, la base de datos reside en un *volumen* persistente que se monta en el contenedor de Postgres, y se prevé incorporar copias de seguridad diarias en AWS S3. Los consumos de vino permanecen, alternativamente, en la nube de Vitte.



## +6. Capítulo 5 — AGREGAR al final

> La dependencia de un sistema de terceros, como lo es Vitte, es una cuestión que puede traer problemas sin previo aviso, aun habiendo sido discutida con el cliente. Mientras tal sistema siga en línea y tenga períodos bajos de caída, los cambios que pueda tener son, muy probablemente, solucionables desde el software y requerirían un tiempo corto de retrabajo. El cambio más importante que puede suceder es que el fabricante discontinúe su nube. En ese caso, será necesario reemplazar el firmware de control, lo que daría lugar a un nuevo proyecto con otros alcances.



## 7. Figuras — REEMPLAZAR imagen


| Figura | Archivo en `figuras_v2/`                     |
| ------ | -------------------------------------------- |
| 2.1    | `vitte.png`                                  |
| 3.4    | `login.png`                                  |
| 3.5    | `tapeo.png`                                  |
| 3.7    | `modelo_logico_rotado.png` (página completa) |
| 3.8    | `capas.png`                                  |
| 3.9    | `recepcion.png`                              |
| 3.10   | `salida.png`                                 |
| 3.11   | `vitte_estados.png`                          |




## +8. Sección 1.4.2, párrafo "Quedaron fuera del alcance…" — AGREGAR al final

> También quedó fuera del alcance el reemplazo del programa o de la electrónica de las dispensadoras. Fue la alternativa considerada con más fuerza al plantear el proyecto con el cliente, pero al presentarse este trabajo ya se había comprobado la viabilidad de integrar Vitte consumiendo sólo su API.



## +9. Sección 2.4.2, después de la Tabla 2.1 — AGREGAR

> De las operaciones en uso, solo una se obtuvo observando el tráfico de la tablet: la búsqueda de cliente por tarjeta. El resto, desde la versión web.


## +10. Sección 3.1.4, caso de uso "Cobrar y cerrar orden" — AGREGAR flujo alternativo al final

> - Flujo alternativo, cierre sin conexión: si Vitte no está disponible, el sistema informa que los consumos de vino pueden estar incompletos y muestra cuándo se actualizaron por última vez. A criterio del cajero, la orden puede cerrarse forzosamente, con confirmación previa. La orden queda identificada como cerrada sin conexión.
