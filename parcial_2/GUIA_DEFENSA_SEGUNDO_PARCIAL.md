# Guía de Exposición y Defensa Oral — Segundo Parcial
**Materia:** Programación Eficiente — Universidad Blas Pascal (UBP)  
**Proyecto:** Detector de Transacciones Sospechosas (Refactorización, Observabilidad y Rendimiento)  
**Recurso de apoyo visual:** Presentación interactiva en [`presentacion/index.html`](file:///home/franco/Repositories/PE/PE/parcial_2/presentacion/index.html)

---

## 🎯 Estrategia General para la Exposición

1. **Duración recomendada:** Entre 10 y 12 minutos en total (~40 a 50 segundos por diapositiva).
2. **Tono y postura:** Seguridad técnica, vocabulario formal de ingeniería de software (complejidades asintóticas, principios SOLID, patrones de diseño, buffers de E/S, profiling) pero **explicando "por encima"** para no perder agilidad.
3. **Regla de oro ante la profesora:** Explica la idea conceptual clara y el resultado medido. Si la profesora quiere profundizar, el detalle fino está en esta guía para responder al instante con fundamentos sólidos.
4. **Navegación de la presentación:**
   - Flechas `←` y `→` o botones en barra inferior.
   - **Click en cualquier captura** para abrir el Lightbox con zoom ampliado.
   - Tecla `Escape` o click fuera de la imagen para cerrar el zoom.

---

## 📋 Resumen Rápido de Comandos para Demostración en Vivo

Si la profesora pide: *"A ver, correlo en vivo"*, abre la terminal en `parcial_2/` con el entorno virtual activo:

```bash
cd /home/franco/Repositories/PE/PE/parcial_2
source .venv/bin/activate

# 1. Pruebas unitarias completas (15 tests en ~0.14 s)
pytest -v

# 2. Análisis estático de código (PEP 8 sin errores)
flake8 .

# 3. Profiling SnakeViz
python main.py perfilado --transacciones 5000
snakeviz resultados/perfilado_optimizado.prof

# 4. Archivo grande de 100 000 transacciones y métricas psutil
python main.py generar-archivo --transacciones 100000 --salida datos/tx_grande.csv
python main.py analizar-archivo datos/tx_grande.csv --lote 10000

# 5. Generación de documentación HTML con Sphinx
sphinx-build -b html docs docs/_build/html
```

---

## 🖼️ Guion Slide por Slide (Qué decir y cómo defenderlo)

---

### Diapositiva 0: Portada
**Título:** Detector de Transacciones Sospechosas — Segundo Parcial  
**Subtítulo:** Optimización, observabilidad, refactorización y pruebas

#### 🖥️ Qué muestra la pantalla
- Portada moderna con tags de las tecnologías centrales: *Python, SnakeViz, psutil, Archivos grandes, PEP 8, Sphinx, flake8, Refactorización, pytest*.

#### 🗣️ Qué decir (30 segundos)
> *"Buenas tardes, profesora. En este segundo parcial de Programación Eficiente evolucionamos el sistema de detección de fraudes transaccionales del primer parcial. El objetivo central fue llevar el proyecto de un prototipo en memoria a un sistema con calidad de producción: eliminamos código redundante, incorporamos profiling con SnakeViz, medimos observabilidad en tiempo real con psutil, adaptamos el motor para procesar archivos masivos sin desbordar la memoria RAM mediante streaming y buffers, aplicamos análisis estático con flake8 y formalizamos toda la suite de pruebas unitarias sobre el framework pytest."*

#### 👩‍🏫 Posibles preguntas de la profesora
- **P: ¿Cuáles eran las 4 reglas de fraude que detecta el sistema?**  
  **R:**  
  1. `MONTO_ALTO`: Transacción que supera el límite fijo (1200) o la media más 3 desviaciones estándar del usuario ($z\text{-score} > 3$).  
  2. `RAFAGA`: Más de 5 transacciones en menos de 60 segundos por el mismo usuario.  
  3. `REPETICION`: 3 o más operaciones con idéntico monto y comercio en una ventana de 300 segundos (5 minutos).  
  4. `UBICACION_SOSPECHOSA`: Operaciones con ubicaciones geográficas distintas en menos de 120 segundos (viaje físicamente imposible).

---

### Diapositiva 1: Índice Completo
**Título:** ¿Qué vamos a ver? — Los 10 temas solicitados por la cátedra

#### 🖥️ Qué muestra la pantalla
- Grilla ordenada con los 10 puntos evaluados: Redundancia, Profiling, Observabilidad, Archivos Grandes, PEP 8, Sphinx, flake8, Refactorización, Testing y Framework pytest.

#### 🗣️ Qué decir (20 segundos)
> *"La presentación está estructurada exactamente siguiendo los 10 temas solicitados por la cátedra. Cada punto no es solo una mención teórica, sino que está implementado en el código fuente, validado con capturas reales y contrastado empíricamente."*

---

### Diapositiva 2: Panorama General (Diff de Cambios)
**Título:** Parcial 1 → Parcial 2 (Resumen git diff)

#### 🖥️ Qué muestra la pantalla
- Bloque estilo terminal Git Diff con las mejoras estructurales entre ambas versiones.

#### 🗣️ Qué decir (40 segundos)
> *"En esta vista panorámica resumimos los cambios arquitectónicos clave. En el Parcial 1 teníamos constantes dispersas, funciones monolíticas como `_detectar_grupo` que mezclaban colas, contadores y persistencia, y el sistema cargaba la totalidad de los datos en la memoria RAM. Para este parcial centralizamos la configuración en dataclasses inmutables, encapsulamos el estado de cada usuario en una clase específica, unificamos la duplicación en CLI y persistencia CSV aplicando el principio DRY, y construimos un pipeline de procesamiento por streaming que permite procesar volúmenes arbitrariamente grandes con memoria constante."*

#### 👩‍🏫 Posibles preguntas de la profesora
- **P: ¿Por qué dicen que el Parcial 1 no era escalable en memoria?**  
  **R:** Porque `generar_transacciones` y `detectar_inicial` exigían tener una lista de objetos `Transaccion` completa en memoria viva. Con 5.000 transacciones no hay problema, pero con 10 o 50 millones se produce un *Out Of Memory* (OOM). La versión 2 resuelve esto con generadores `yield` y streaming por lotes.

---

### Diapositiva 3: Tema 1 — Código Redundante (Parte 1: Configuración DRY)
**Título:** Configuración centralizada (DRY) — `ConfiguracionDeteccion`

#### 🖥️ Qué muestra la pantalla
- Código comparativo: constantes globales sueltas en `detectores.py` vs `@dataclass(frozen=True, slots=True)` en `configuracion.py`.

#### 🗣️ Qué decir (35 segundos)
> *"El primer tema abordado fue la eliminación de código redundante mediante el principio DRY (Don't Repeat Yourself). Antes, los umbrales de negocio —como los 60 segundos de ráfaga o los 1200 pesos de monto fijo— estaban dispersos como variables globales y se propagaban manualmente como argumentos en múltiples funciones. Lo refactorizamos en `ConfiguracionDeteccion`, un dataclass que centraliza los parámetros en un único punto de verdad."*

#### 👩‍🏫 Posibles preguntas de la profesora
- **P: ¿Por qué usaron `frozen=True` y `slots=True` en el dataclass?**  
  **R:**  
  - `frozen=True` hace que las instancias sean **inmutables**, garantizando que ninguna parte del código altere accidentalmente los umbrales de negocio durante la ejecución o entre tests concurrentes.  
  - `slots=True` suprime la creación del diccionario dinámico `__dict__` por instancia en Python, reduciendo la huella de memoria y acelerando el acceso a los atributos a nivel de bytecode CPython.

---

### Diapositiva 4: Tema 1 — Código Redundante (Parte 2: EstadoDeteccionUsuario)
**Título:** `EstadoDeteccionUsuario` (Encapsulamiento OOP)

#### 🖥️ Qué muestra la pantalla
- Código comparativo: variables locales repetidas para colas y diccionarios vs clase `EstadoDeteccionUsuario`.

#### 🗣️ Qué decir (40 segundos)
> *"Siguiendo con la eliminación de código redundante, antes la lógica para depurar las ventanas deslizantes de tiempo se duplicaba en varios puntos. Creamos la clase `EstadoDeteccionUsuario`. Esta clase encapsula las tres colas `deque` del usuario —para ráfagas, repeticiones y ubicaciones— junto a su lógica temporal. Lo más importante: esta misma clase procesa tanto las transacciones en memoria RAM del benchmark como los lotes que llegan del archivo CSV en streaming, logrando una reutilización del 100% sin clonar código."*

#### 👩‍🏫 Posibles preguntas de la profesora
- **P: ¿Por qué `deque` y no una lista estándar de Python (`list`)?**  
  **R:** Porque una ventana deslizante necesita expulsar los elementos vencidos por el extremo izquierdo (`popleft()`). En un `list`, hacer `pop(0)` desplaza todos los elementos restantes en memoria, lo que cuesta $O(k)$ donde $k$ es el tamaño de la ventana. En un `collections.deque` (implementado internamente en C como una lista doblemente enlazada de bloques), `popleft()` y `append()` se ejecutan en tiempo estrictamente constante $O(1)$.

---

### Diapositiva 5: Tema 2 — Optimización y Profiling (SnakeViz)
**Título:** SnakeViz — Profiling visual interactivo

#### 🖥️ Qué muestra la pantalla
- Captura de pantalla de SnakeViz mostrando la versión optimizada (`detectar_optimizado` en 0.0205 s).
- Lista de características y comandos utilizados.

#### 🗣️ Qué decir (40 segundos)
> *"Para el tema 2 usamos SnakeViz junto con el módulo estándar `cProfile`. SnakeViz nos permite visualizar gráficamente los archivos `.prof` generados por el perfilador en el navegador mediante diagramas de carámbanos (icicle charts). Cada bloque horizontal representa una función y su ancho es proporcional al tiempo acumulado de CPU. Esto nos permitió hacer un diagnóstico científico del call-stack sin adivinar dónde estaba el cuello de botella."*

#### 👩‍🏫 Posibles preguntas de la profesora
- **P: ¿Qué ventaja tiene SnakeViz frente a simplemente leer el `pstats` en la terminal?**  
  **R:** La salida de texto de `pstats` lista funciones en orden plano; SnakeViz reconstruye visualmente la jerarquía completa del árbol de llamadas (*call tree*). Permite ver con claridad qué función padre está invocando repetidamente a una hija costosa y explorar interactivamente haciendo click en cada función.

---

### Diapositiva 6: Tema 2 — Cuello de Botella Identificado
**Título:** SnakeViz: `ordenar_burbuja` como bottleneck principal

#### 🖥️ Qué muestra la pantalla
- Captura de SnakeViz versión inicial con el bloque gigante rojo de `ordenar_burbuja`.
- Comparativa numérica de `cProfile`: 344.111 llamadas y 2.575 s vs 86.384 llamadas y 0.051 s.

#### 🗣️ Qué decir (45 segundos)
> *"En esta captura se aprecia con total claridad el diagnóstico: en la versión inicial, la función `ordenar_burbuja` consumía el 51% del tiempo total del programa —más de 1 segundo sobre 2.5 segundos totales con 5.000 transacciones. Detectado el cuello de botella, aplicamos dos optimizaciones algorítmicas: reemplazamos Bubble Sort $O(n^2)$ por Quicksort $O(n \log n)$ e introdujimos una memoria caché LRU para los perfiles estadísticos de los usuarios. El resultado fue drástico: el tiempo de ejecución cayó de 2.575 segundos a solo 0.051 segundos, una aceleración de 50 veces comprobada por el profiler."*

#### 👩‍🏫 Posibles preguntas de la profesora
- **P: ¿Por qué es obligatorio ordenar las transacciones si ya vienen simuladas?**  
  **R:** En la vida real, las transacciones llegan a los servidores bancarios desordenadas por latencias de red o colas asíncronas. Para evaluar ventanas temporales deslizantes (60s, 120s, 300s), el algoritmo requiere que los eventos estén en orden cronológico ($t_i \ge t_{i-1}$); de lo contrario, expulsaría transacciones válidas o admitiría eventos fuera de ventana.
- **P: ¿Cómo funciona el cache LRU de perfiles?**  
  **R:** La clase `CachePerfiles` almacena la media, desviación estándar y límite de cada usuario en un diccionario con capacidad máxima (1024 entradas). Si el perfil ya se calculó para ese usuario, se devuelve en $O(1)$ sin tener que recalcular la suma y la raíz cuadrada de la varianza en cada transacción.

---

### Diapositiva 7: Resultados Medidos — Comparativa de Versiones
**Título:** Comparación empírica (5 000 transacciones)

#### 🖥️ Qué muestra la pantalla
- Tabla de resultados: Inicial (2.855s), Estructura (0.160s), Algoritmo (0.055s), Concurrencia (0.198s), Final (0.051s).
- Métricas: 56× de aceleración y 9/9 alertas idénticas en todas las versiones.

#### 🗣️ Qué decir (45 segundos)
> *"En esta tabla validamos empíricamente la evolución del rendimiento con 5.000 transacciones. La versión inicial tardaba 2.85 segundos. Al mejorar las estructuras de datos con diccionarios y deques bajó a 0.16 segundos. Al cambiar el algoritmo a Quicksort con caché bajó a 0.055 segundos. Noten un detalle clave: la versión paralela con 2 trabajadores tardó 0.198 segundos, siendo cuatro veces más lenta que la secuencial óptima. Por eso, la versión final elegida es la secuencial optimizada, logrando 56 veces de aceleración respecto al baseline y garantizando que las 9 alertas detectadas sean exactamente idénticas en todas las versiones."*

#### 👩‍🏫 Posibles preguntas de la profesora (¡PREGUNTA CLÁSICA DE EXAMEN!)
- **P: ¿Por qué la versión con multiprocessing fue MÁS LENTA que la secuencial?**  
  **R:** Por el **overhead de IPC (*Inter-Process Communication*) y serialización**. En Python, `ProcessPoolExecutor` crea procesos independientes para sortear el GIL (*Global Interpreter Lock*). Pero para pasarle las transacciones a cada proceso hijo y recibir las alertas de vuelta, Python debe serializar y deserializar los objetos usando `pickle` a través de pipes del sistema operativo. Para 5.000 transacciones, el tiempo consumido en serializar datos y sincronizar procesos supera ampliamente el tiempo que tarda Quicksort en un solo núcleo. El paralelismo solo conviene cuando el costo computacional por tarea es significativamente mayor que el costo de comunicación entre procesos.

---

### Diapositiva 8: Resultados Medidos — Escalabilidad
**Título:** Escalabilidad — $O(n^2)$ vs $O(n \log n)$

#### 🖥️ Qué muestra la pantalla
- Gráficos de barras comparando el tiempo inicial vs optimizado a 1.000, 2.500 y 5.000 transacciones.
- Métricas de aceleración: 24× a 1.000 tx, 62× a 2.500 tx y 148× a 5.000 tx.

#### 🗣️ Qué decir (35 segundos)
> *"Para comprobar que la optimización no era un caso aislado de 5.000 transacciones, corrimos pruebas de escalabilidad con tres volúmenes distintos. Mientras que la versión cuadrática explota exponencialmente pasando de 0.11 segundos a 2.67 segundos, la versión optimizada apenas sube de 0.005 a 0.018 segundos. La brecha de ventaja crece a medida que aumenta el volumen: a 1.000 transacciones es 24 veces más rápida, y a 5.000 transacciones llega a ser 148 veces superior."*

---

### Diapositiva 9: Tema 3 — Herramientas Generales de Observabilidad (psutil)
**Título:** `psutil` — Alternativa a New Relic y Elastic APM

#### 🖥️ Qué muestra la pantalla
- Captura de pantalla de la terminal con las métricas de `psutil`.
- Tarjeta de justificación técnica: ¿Por qué `psutil` y no New Relic o Elastic APM?

#### 🗣️ Qué decir (45 segundos)
> *"Para el tema 3, la consigna pedía herramientas generales de observabilidad y mencionaba plataformas como New Relic o Elastic APM. Nosotros optamos por `psutil`, y la decisión responde a un criterio de ingeniería de software: **proporcionalidad arquitectónica**. New Relic o Elastic APM están diseñados para arquitecturas de microservicios distribuidos 24/7 en la nube; requieren daemons residentes, cuentas cloud y consumo de red. Nuestro detector es una herramienta CLI que procesa lotes locales. `psutil` nos brinda acceso directo y no invasivo a las métricas del sistema operativo: memoria física RSS, tiempo de CPU de usuario y de sistema, y bytes de entrada/salida leídos y escritos directamente sobre el PID del proceso."*

#### 👩‍🏫 Posibles preguntas de la profesora
- **P: ¿Cómo implementaron la medición en el código?**  
  **R:** Creamos el módulo `monitoreo.py` con la función `medir_recursos()`. Esta función toma un `Callable`, lanza un hilo secundario *daemon* que sondea la memoria física `rss` cada 10 milisegundos (`intervalo=0.01`) para registrar el pico máximo de memoria consumido, y toma snapshots de los tiempos de CPU y contadores de E/S (`io_counters`) antes y después de ejecutar la operación.

---

### Diapositiva 10: Tema 4 — Archivos Grandes (Batching, Buffer y Streaming)
**Título:** Batching · Buffer · Procesamiento Streaming en Dos Pasadas

#### 🖥️ Qué muestra la pantalla
- Dos capturas reales: generación del CSV de 100.000 transacciones y posterior análisis por lotes de 10.000 con reporte de `psutil`.
- Cuadro destacado: **100 000 transacciones procesadas en 0.50 s y consumiendo apenas 39.52 MB de RAM**.

#### 🗣️ Qué decir (50 segundos)
> *"El tema 4 fue uno de los mayores desafíos técnicos: procesar archivos grandes sin agotar la memoria. Diseñamos una solución basada en tres pilares: primero, un buffer de E/S de 1 MB (`buffering=1024*1024`) en la lectura y escritura de CSV para minimizar las llamadas al sistema del sistema operativo. Segundo, generadores con `yield` mediante `leer_transacciones_csv()` y `agrupar_en_lotes()`, que entregan lotes configurables de, por ejemplo, 10.000 elementos. Y tercero, un procesamiento en dos pasadas con memoria $O(1)$: la primera pasada calcula la media y varianza con el algoritmo incremental de Welford sin almacenar transacciones en RAM; la segunda pasada evalúa las alertas manteniendo el estado entre lotes. Como se ve en la captura, procesamos 100.000 transacciones en solo 0.50 segundos con apenas 39 MB de memoria."*

#### 👩‍🏫 Posibles preguntas de la profesora (¡PREGUNTA TRAMPA!)
- **P: Si procesan por lotes de 10.000 transacciones, ¿qué pasa si una ráfaga o repetición ocurre en el límite entre el lote 1 y el lote 2? ¿No se pierden alertas?**  
  **R:** **No, no se pierde ninguna alerta.** Esa es la gran ventaja del diseño refactorizado: el diccionario `estados` con los objetos `EstadoDeteccionUsuario` se instancia **afuera** del bucle de lotes. Cuando termina el primer lote y empieza el segundo, las colas `deque` del usuario conservan exactamente las transacciones anteriores dentro de su ventana temporal de 60 o 300 segundos. Hay continuidad temporal perfecta entre lotes.
- **P: ¿Qué es el algoritmo de Welford y por qué lo usaron?**  
  **R:** Está en la clase `AcumuladorPerfil`. Es un método numérico online que calcula la media y la varianza acumulada en un solo paso ($O(n)$ tiempo, $O(1)$ memoria). Evita tener que guardar la lista de montos en RAM para calcular la desviación típica y además evita los errores de cancelación catastrófica por punto flotante que tiene la fórmula clásica $\sum x^2 - \frac{(\sum x)^2}{N}$.
- **P: ¿Por qué no usaron Pandas o Polars?**  
  **R:** Porque para la naturaleza del problema queríamos control explícito del consumo de recursos y demostrar la capacidad de procesar streaming con la biblioteca estándar de Python sin sobrecargar con dependencias pesadas de análisis tabular en memoria.

---

### Diapositiva 11: Temas 5 y 7 — Legibilidad, PEP 8 y Análisis de Calidad (flake8)
**Título:** PEP 8 · Nombres descriptivos · flake8

#### 🖥️ Qué muestra la pantalla
- Captura de `flake8` detectando la advertencia de formato `E265` en un comentario y guiando su corrección.
- Captura de código limpio con nombres autodocumentados y docstrings estructurados.

#### 🗣️ Qué decir (40 segundos)
> *"Para los temas 5 y 7 abordamos legibilidad, PEP 8 y análisis estático de calidad. Integramos `flake8` configurado en el archivo `.flake8` para auditar todo el proyecto. En la captura vemos cómo el linter detectó un error `E265` debido a un comentario sin espacio `#texto`, obligando a corregirlo a `# texto`. Además, el código fue redactado con nombres autodocumentados —como `tamanio_buffer` o `ultimo_instante`—, tipado estricto con `type hints` de Python 3.10 y docstrings en todas las funciones y clases."*

#### 👩‍🏫 Posibles preguntas de la profesora
- **P: ¿Qué configuración tiene `.flake8`?**  
  **R:** Establece un límite de longitud de línea de 88 caracteres (estándar moderno compatible con Black) y excluye carpetas de entorno virtual (`.venv`, `build`, `docs/_build`). Garantiza que el código no tenga imports sin usar (`F401`), variables no referenciadas o problemas de indentación.

---

### Diapositiva 12: Tema 6 — Generación de Documentación (Sphinx)
**Título:** Sphinx — Documentación HTML desde docstrings

#### 🖥️ Qué muestra la pantalla
- Captura de la compilación exitosa de Sphinx en terminal (`sphinx-build -b html`).
- Captura del sitio web navegable generado en `docs/_build/html/index.html`.

#### 🗣️ Qué decir (35 segundos)
> *"Para el tema 6 implementamos generación automática de documentación técnica con Sphinx. Configuramos las extensiones `autodoc`, `napoleon` y `viewcode` en `docs/conf.py`. Sphinx inspecciona el código fuente en tiempo de compilación, extrae las firmas, tipos y docstrings, y genera un sitio web estático navegable con buscador integrado y enlaces directos al código fuente de cada módulo."*

#### 👩‍🏫 Posibles preguntas de la profesora
- **P: ¿Por qué usaron la extensión `napoleon`?**  
  **R:** Porque permite escribir docstrings legibles en formato Google Style o NumPy Style con secciones `Args:`, `Returns:` y `Raises:` sin tener que llenar el código de sintaxis pesada de reStructuredText (`:param ...:`).

---

### Diapositiva 13: Tema 8 — Refactorización y Principios de Diseño
**Título:** Refactorización y Principios de Diseño (SRP, DRY, Desacoplamiento)

#### 🖥️ Qué muestra la pantalla
- Código comparativo: Monolito acoplado de más de 120 líneas en `detectar_inicial` vs funciones atómicas con responsabilidades claras.
- Caja con principios SRP, DRY y desacoplamiento para streaming.

#### 🗣️ Qué decir (40 segundos)
> *"En el tema 8 de refactorización aplicamos formalmente principios de diseño. El detector inicial violaba el Principio de Responsabilidad Única (SRP): una sola función agrupaba por usuario, calculaba promedios, ejecutaba bubble sort, administraba tres colas y generaba las alertas en un bloque de 120 líneas. Lo descompusimos en funciones atómicas: particionado, cálculo estadístico online, caché LRU y el evaluador de ventanas. Gracias a este desacoplamiento, la función `iterar_alertas_csv()` pudo reutilizar exactamente la misma lógica para procesar archivos grandes en streaming sin duplicar código."*

---

### Diapositiva 14: Tema 9 — Testing con pytest y psutil
**Título:** pytest + psutil — Pruebas y validación de recursos

#### 🖥️ Qué muestra la pantalla
- Código de fixtures con scope de módulo y `@pytest.mark.parametrize` probando tamaños de lote 1, 7, 100 y 1000.
- Captura real de pytest: **15 passed in 0.14s**.

#### 🗣️ Qué decir (45 segundos)
> *"Para el tema 9 implementamos una suite integral con `pytest`. Son 15 pruebas unitarias que se ejecutan en apenas 0.14 segundos. Destacamos dos técnicas avanzadas: primero, el uso de fixtures con ámbito de módulo (`scope='module'`) para reutilizar el set de transacciones sin recalcularlo en cada test. Segundo, parametrización con `@pytest.mark.parametrize` probando tamaños de lote de 1, 7, 100 y 1.000 transacciones contra una ejecución en memoria, validando matemáticamente que el resultado de alertas es 100% idéntico sin importar el tamaño del lote. Además, integramos `psutil` dentro de un test unitario para verificar que el sistema capture correctamente las métricas de memoria RSS."*

#### 👩‍🏫 Posibles preguntas de la profesora
- **P: ¿Por qué probaron con un lote de tamaño 1 y con tamaño 7?**  
  **R:** Tamaño 1 es el caso extremo inferior (lote mínimo posible, prueba estrés en la frontera). Tamaño 7 es un número primo impar que deliberadamente desincroniza los bloques con respecto a ventanas temporales y múltiplos decimales. Si las alertas coinciden tanto para 1, 7, 100 como para 1.000, queda matemáticamente demostrado que no hay fugas ni duplicaciones en los bordes de los lotes.

---

### Diapositiva 15: Tema 10 — Uso de Framework (pytest)
**Título:** pytest como Framework de Desarrollo y Testing

#### 🖥️ Qué muestra la pantalla
- Configuración central en `pyproject.toml` (`[tool.pytest.ini_options]`).
- Justificación de por qué `pytest` califica como framework: Inversión de Control, fixtures inyectadas, assert rewriting y ecosistema de plugins.

#### 🗣️ Qué decir (40 segundos)
> *"Para cerrar con el tema 10, justificamos la adopción de `pytest` no solo como ejecutor de pruebas, sino como un verdadero **framework**. A diferencia de una biblioteca convencional o del módulo `unittest`, `pytest` implementa Inversión de Control (IoC): él controla el ciclo de vida de la ejecución, descubre automáticamente los tests, reescribe el bytecode de las aserciones (`assert rewriting`) para generar mensajes de depuración detallados, y administra inyección de dependencias modular mediante fixtures. Todo está centralizado en el estándar moderno `pyproject.toml`, donde además integramos soporte para plugins como `pytest-cov` para cobertura de código."*

#### 👩‍🏫 Posibles preguntas de la profesora
- **P: ¿Cuál es la diferencia conceptual entre una librería y un framework?**  
  **R:** La **Inversión de Control** (*Hollywood Principle: "Don't call us, we'll call you"*). En una librería, el código del desarrollador llama a las funciones de la librería cuando las necesita. En un framework como `pytest`, el framework toma el control principal del hilo de ejecución, orquesta el ciclo de vida y llama al código de prueba del usuario a través de convenciones, marcadores y fixtures inyectadas.

---

## 🧭 Matriz de Mapeo: Los 10 Requisitos de la Cátedra vs Código Fuente

| # | Tema Solicitado | Módulo / Archivo | Elemento en el Código | Diapositiva |
|---|---|---|---|---|
| **1** | Código redundante | `configuracion.py` y `detectores.py` | `ConfiguracionDeteccion`, `EstadoDeteccionUsuario`, DRY en CLI | **Slide 3 y 4** |
| **2** | Optimización y profiling | `perfilado.py` y `resultados/` | `cProfile`, exportación `.prof`, SnakeViz interactivo, Quicksort | **Slide 5 y 6** |
| **3** | Herramientas generales | `monitoreo.py` | `psutil.Process()`, RSS física, CPU user/sys, E/S de disco | **Slide 9** |
| **4** | Archivos grandes | `archivos.py` | Buffer 1 MB, `yield` streaming, batching, Welford online | **Slide 10** |
| **5** | Legibilidad y mantenibilidad | Todo el proyecto | Nombres autodocumentados, docstrings con tipos, PEP 8 | **Slide 11** |
| **6** | Generación de documentación | `docs/` | Sphinx con `autodoc`, `napoleon`, `viewcode`, HTML navegable | **Slide 12** |
| **7** | Análisis de calidad | `.flake8` | `flake8 .` (sin errores ni advertencias de estilo) | **Slide 11** |
| **8** | Refactorización | `detectores.py` | Descomposición de monolito en SRP, desacoplamiento de streaming | **Slide 13** |
| **9** | Testing | `tests/` | 15 tests, fixtures modulares, `@pytest.mark.parametrize`, psutil | **Slide 14** |
| **10** | Uso de framework | `pyproject.toml` | pytest con Inversión de Control, `pytest-cov`, plugins | **Slide 15** |

---

## 💡 Consejos Finales para Obtener la Máxima Nota

1. **Si te preguntan por números:** Recuerda los dos más contundentes:
   - **50× / 56× de aceleración** en 5.000 transacciones (de 2.85s a 0.051s).
   - **100.000 transacciones** en archivo CSV analizadas en **0.50 segundos con solo 39.5 MB de RAM**.
2. **Si te preguntan por las alertas:** Resalta que la exactitud funcional nunca se sacrificó por velocidad: **todas las versiones detectan exactamente 9 alertas de 9 posibles**.
3. **Muestra entusiasmo por las herramientas modernas:** Destaca cómo el estándar `pyproject.toml`, `psutil`, `SnakeViz`, `Sphinx` y `pytest` conforman un entorno de desarrollo profesional en Python.
