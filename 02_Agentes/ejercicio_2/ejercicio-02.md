# Ejercicio 2 — Descripción PEAS de agentes inteligentes


## Objetivo

Para cada una de las **8 aplicaciones** listadas abajo, redacta una descripción
PEAS completa y coherente. Debes pensar como diseñador del agente: qué optimiza,
dónde actúa, con qué puede mover o modificar el mundo, y qué puede observar.

## Aplicaciones a analizar

Describe PEAS para cada una de estas aplicaciones:

1. **Asistente virtual de voz** (p. ej. Siri, Alexa o Google Assistant en un altavoz inteligente).
    - **Performance**: Escucha de forma correcta la petición del usuario, realiza exactamente la actividad que pide el usuario, rapidez con la que completa la petición y da una respuesta.
    - **Enviroment**:Habitaciones de casa u oficinas, es observable porque podrá escuchar todos los sonidos de la habitación y determinista ya que cada petición deberá arrojar el mismo resultado. 
    - **Actuators**: Controles de reproducción (volumen, play/pausa, avanzar/retroceder), prender y apagar temporizadores, mandar alertas(bocina o en pantalla si cuenta con una), conectarse a otros servicios (crear eventos de calendario, consultar el clima, poner una canción,etc.)
    - **Sensors**: Micrófonos, pantalla táctil(si cuenta con una), sensores de movimiento. 
2. **Robot aspirador doméstico** (p. ej. Roomba u otro robot que limpia pisos de un departamento).
    - **Performance**: Deja el piso realmente limpio, realiza la limpieza rápido y de forma silenciosa, eficacia energética y uso de agua (no limpia cuando el piso ya está limpio)
    - **Enviroment**: Habitaciones, interacción con personas y mascotas. Es parcialmente observable, ya que guarda en la memoria la dimensión y características de la habitación, pero no sabe donde se encuentran personas y mascotas con exactitud en todo momento. Es dinámico, ya que la situación de la habitación puede cambiar de forma repentina (dejar caer objetos por ejemplo) y es discreto, ya que el agente tiene un conjunto finito de acciones, por ejemplo: limpiar, avanza, regresar a base y autolavado. 
    - **Actuators**: Girar escobillas (para limpiar el piso), movimiento del agente (avanzar, detener, dar vueltas de 90° y 180°), autolimpiar (cuando en la base gira las escobillas para limpiarlas), emitir alertas (como cuando se atora, cae o voltea, cuando las escobillas requieren reemplazo o el aparato requiere mantenimiento)
    - **Sensors**: Sensor de movimiento, cámara, gps, termómeto (para identificar sobrecalentamiento en el aparato).
3. **Sistema de recomendación de streaming** (p. ej. Netflix o Spotify que sugiere películas o canciones).
    - **Performance**: el usuario ve la película recomendada completa, el usuario marca la película como "agregar a mi lista". La película sugerida fue del agrado del usuario (le dio una puntuación buena o un "like")
    - **Enviroment**: Aplicación de streaming, con la lista de contenido visto por el usuario y el porcentaje del contenido que el usuario vio, así como el catálogo completo de la plataforma y el contenido visto por otro usuarios y sus características (edad, trabajo, tiempo de straming, etc.). Considero que es un ambiente completamente observable ya que puede tener acceso a toda la información de la aplicación en todo momento, es discreto, determinista y estático, ya que el catálogo no cambia de un momento a otro y se puede sugerir solamente películas dentro del catálogo. 
    - **Actuators**: Enviar notificaciones al usuario con las recomendaciones, mostrar anuncios o trailers de películas, colocar películas en los banners de las aplicaciones.
    - **Sensors**: Leer información de las películas del usuario y de los usuarios con características similares. Si la aplicación está en un dispositivo móvil con cámara, puede la cámara ver si el usuario esta prestando atención al contenido. 
4. **Vehículo autónomo en ciudad** (conducción sin conductor en calles urbanas con tráfico y peatones).
    - **Performance**: Seguridad de los pasajeros, respeta los reglamentos (vialidad y límites de velocidad), lleva a los pasajeros al destino correcto, comodidad de los pasajeros, eficiencia energética/ Ahorro de energía o combustible. 
    - **Enviroment**: Calles, carreteras, puentes; las condiciones cambian con el clima, existe interacción con personas y otros vehículos. Es parcialmente observable ya que puede ver lo que esta cerca del vehículo, pero puede ser que no detecte correctamente algún objeto pequeño o zonas con poca luz. Es dinámico y continuo, ya que el ambiente puede cambiar repentinamente y hay una infinita cantidad de condiciones. 
    - **Actuators**: Movimiento (dar marcha/retroceder, dar vuelta a la derecha/Izquiera, acelerar/desacelerar), enviar alertas a los pasajeros (por peatones o objetos en el paso, avisos generales del vehículo o mantenimientos), claxón para alertas fuera del vehículo, hacer llamadas de emergencia o pedir ayuda, encender/apagar luces y estéreo. 
    - **Sensors**: cámaras, sensores de movimiento, nivel de combustible/batería, termómetros, acelerómetros, gps, sensores de presión de llantas, sensores de luz.
5. **Agente de trading algorítmico en bolsa** (compra y venta automática de acciones en mercados financieros).
    - **Performance**: Si al final del periodo (día o semana) se registra una ganancia en el portafolio. Hacerlo con el menor número de movimientos de compra venta-posibles. Mantener un riesgo de pérdida bajo/ buena diversificación de portafolio. Elige comprar-vender de forma adecuada de acuerdo con la puntuación/confianza de las acciones, si se vende a precio alto y se compra a precio bajo.
    - **Enviroment**: Mercado financiero de acciones, el cual podemos considerar completamente observable, ya que podemos conocer el precio de las acciones en todo momento. No es determinista, es dinámico y continuo, ya que el precio de las acciones fluctuan en cuestión de minutos/segundos y lo hacen de forma aleatoria con el paso del tiempo, podemos considerarlo secuencial, ya que dependiendo del comportamiento previo podemos ver tendencias a la baja o a la alta. 
    - **Actuators**: Acciones de comprar o vender las acciones, enviar alertas al usuario de caída o subida de precios promedios, crear gráficos cada determinado tiempo para observar el comportamiento de precios, generar reportes al final de cada periodo(día/semana) de los movimientos y sus resultados. 
    - **Sensors**: Programa de lectura de precios de acciones en tiempo real. 
6. **Sistema de diagnóstico médico asistido por IA** (apoya a un médico a interpretar síntomas e imágenes clínicas).
    - **Performance**: Realiza un diagnóstico adecuado, sin demorar mucho tiempo. Para cada diagnóstico dar una justificación con sustento médico real. Minimizar la probabilidad de un falsonegativo(equivocarse) o minimizar el costo análisis futuros, como requerir menos estudios que pueden ser costosos.  
    - **Enviroment**: Conjunto de base de datos de información del paciente. Considero sería un ambiente parcialmente observable, ya que el agente tendría acceso a los estudios previos del paciente pero no conoce la enfermedad o condición real del paciente. Si se consiera que el agente intentará inferir sobre la enfermedad del paciente sería un ambiente no determinista, ya que hay muchas probabilidades de enfermedad considerando los mismos síntomas. Lo considero de igual forma un ambiente discreto, ya que hay un conjunto finito de posibles diagnósticos. 
    - **Actuators**: Crear gráficos para mostrar alguna condición observadda en el paciente. Colocar puntos en imágenes para señalar diagnósticos. Generar reportes o solicitudes de análisis adicionales. Sonar alarmas si detecta un condición crítica o peligrosa del paciente para actuar rápido. 
    - **Sensors**: Cámara, digitalizadores (escáneres), Si consideramos que el agente evalúe físicamente al paciente, puede requerir termómetro, medidor de presión sanguínea, entrada de lectura de electrocardiograma. Software de lectura de radiografías médicas. 
7. **Dron de inspección de infraestructura** (revisa grietas, corrosión o fugas en puentes, tuberías o líneas eléctricas).
    - **Performance**: Identifica los desperfectos de forma precisa, indicando tipo de desperfecto, ubicación en la estructura y su gravedad. 
    - **Enviroment**: Si el dron es para espacios abiertos o interperie, esta expuesto a corrientes de aire, objetos colgantes o con movimiento, por lo que el ambiente es parcialmente observable, ya que hay espacios ciegos que el agente no puede ver por sus sensores en todo momento. Puede cambiar el entorno con el clima, por lo que no es determinista y continuo, ya que los cambios en el ambiente pueden ser aleatorios y cambian continuamente.  
    - **Actuators**: Enviar alertas al usuario cuando encuentra un desperfecto, guardar un registro en una lista para guardar información del desperfecto. Prender/apagar luces o emitir sonidos de alerta. Movimiento de las hélices para subir y bajar altura, ir de derecha a izquierda, rotar sobre su eje. 
    - **Sensors**: Cámaras, sensores de movimiento, sensores infrarrojos para medir distancias, giroscópio para la estabilidad, sensores de altura, gps. 
8. **Agente jugador de ajedrez** (programa que compite contra un humano u otro agente en partidas completas).
    - **Performance**: Tasa de partidas ganadas alta, gana con un número bajo de movimientos, número de piezas perdidas es bajo, se siguen las reglas del juego, elegir la jugada más óptima en cada situación.
    - **Enviroment**: Tablero de Ajedrez, Es totalmente observable, ya que sabemos en todo momento el estado de la partida. Es determinístico, ya que cada pieza siempre realiza el mismo tipo de movimiento y se obtiene el mismo resultado, es estático ya que en lo que el agente actua el tablero se queda igual. Es episódico ya que el tiempo se puede fraccionar en turnos y discreto, ya que las acciones que se pueden realizar es un conjunto finito.  
    - **Actuators**: Mover las piezas de acuerdo con las reglas del juego, realizar enroques, enviar alertas de jaque y jaquemate, generar un formato con todos los movimientos realizados por los jugadores.  
    - **Sensors**: Si es un tablero físico se requiere cámara o un tablero que tiene sensores para conocer las posiciones de las piezas(como en los torneos), si es digital se requiere la lectura de la posición de todas las piezas en cada momento. 

