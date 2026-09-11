# Guía Completa de Presentación: Teoría Rigurosa, Ejemplos Prácticos y Capturas de Código

**Materia:** Programación Eficiente — Primer Parcial  
**Lenguaje:** Python 3.10+ (Biblioteca estándar + Matplotlib opcional para gráficos)  
**Ubicación del Proyecto:** `parcial_1/`

---

## 0. Instrucciones de Ejecución Rápida (Entorno Virtual)

Abre la terminal en la raíz del repositorio y corre:

```bash
cd parcial_1
source .venv/bin/activate
```

### Tabla de Comandos para la Demostración:

| Objetivo | Comando | Qué produce |
|---|---|---|
| **Interfaz Gráfica (Demo)** | `python main.py interfaz` | Ventana nativa Tkinter con grilla de alertas y comparativa visual. |
| **Benchmark Completo** | `python main.py benchmark --transacciones 5000 --trabajadores 2` | Genera tabla en consola, `resultados/comparacion.csv` y gráfico `comparacion_tiempos.png`. |
| **Perfilado Científico** | `python main.py perfilado --transacciones 5000` | Ejecuta `cProfile`, vuelca `.prof` y exporta el top 15 de funciones a `perfilado_resumen.txt`. |
| **Prueba de Escalabilidad** | `python main.py escalabilidad --volumenes 1000 2500 5000` | Mide el crecimiento de $O(n^2)$ vs $O(n \log n)$ y genera `escalabilidad.png`. |
| **Tests de Corrección** | `python -m unittest discover -v` | Valida que todas las versiones detecten exactamente las mismas 9 alertas. |

---

```
                                  MAPA DE LA PRESENTACIÓN
┌──────────────────────────────┬─────────────────────────────┬─────────────────────────────────┐
│ 1. El Problema               │ 2. Diseño Inicial           │ 3. Complejidad Algorítmica      │
│  • Teoría: Reglas & Dominio  │  • Teoría: Arquitectura     │  • Teoría: Deducción O(n²)      │
│  • Práctica: Viaje Imposible │  • Práctica: Pila de Tickets│  • Práctica: Baraja de Cartas   │
├──────────────────────────────┼─────────────────────────────┼─────────────────────────────────┤
│ 4. Algoritmos y Estructuras  │ 5. Memoización y Caching    │ 6. Concurrencia y Paralelismo   │
│  • Teoría: Quicksort & Deque │  • Teoría: LRU Cache & Inval│  • Teoría: GIL vs IPC Multiprocess
│  • Práctica: Fila Supermerc. │  • Práctica: Post-it Cajero │  • Práctica: 4 Empleados Oficina│
├──────────────────────────────┴─────────────────────────────┴─────────────────────────────────┤
│ 7. Perfilado de Código       │ 8. Comparación de Resultados                                  │
│  • Teoría: cProfile & pstats │  • Teoría: perf_counter & tracemalloc                         │
│  • Práctica: La Radiografía  │  • Práctica: Caso CyberMonday (1h vs 0.5s)                     │
└──────────────────────────────┴───────────────────────────────────────────────────────────────┘
```

---

## Diapositiva 1: El Problema

### Fundamento Teórico y Académico
- **Problema formal:** Procesamiento en lote (*batch processing*) y flujo continuo de transacciones financieras no sincronizadas temporalmente para la detección de fraude bancario bajo ventanas de tiempo deslizantes.
- **Interés en programación eficiente:**
  - El volumen de transacciones en infraestructuras financieras escala a miles de eventos por segundo.
  - La llegada de eventos ocurre en orden cronológico arbitrario (desordenados por latencias de red, colas distribuidas o servidores asíncronos).
  - Evaluar ventanas temporales exige ordenamiento y análisis de frecuencias con latencias acotadas en microsegundos para evitar demoras en puntos de venta (POS).
- **Las 4 Reglas de Negocio / Fraude:**
  1. **`MONTO_ALTO` (Anomalía Estadística Gaussiana):**
     - Se computa la media muestral ($\mu = \frac{1}{m}\sum x_i$) y la desviación estándar ($\sigma = \sqrt{\frac{1}{m}\sum (x_i - \mu)^2}$) del usuario.
     - Si la transacción supera el umbral dinámico $\max(1200.0, \mu + 3\sigma)$, se clasifica como anomalía estadística ($z\text{-score} > 3$, cubriendo el 99.7% de la distribución normal).
  2. **`RAFAGA` (Vaciado de Fondos en Ventana Corta):**
     - Detección de $\ge 5$ transacciones del mismo usuario en un intervalo $\Delta t \le 60\text{ s}$.
  3. **`OPERACION_REPETIDA` (Ataque de Replay / Cobros Duplicados):**
     - Detección de $\ge 3$ transacciones con idéntico monto y comercio en $\Delta t \le 300\text{ s}$ (5 minutos).
  4. **`UBICACIONES_SIMULTANEAS` (Viaje Físicamente Imposible / Clonación):**
     - Actividad del mismo usuario desde $\ge 2$ ubicaciones geográficas distintas en $\Delta t \le 120\text{ s}$ (2 minutos).

### Ejemplo Práctico en Lenguaje Natural
> *"Pensemos en el caso de las **Ubicaciones Simultáneas**: Juan compra un café en una estación de servicio de Córdoba a las 10:00:00. Exactamente 30 segundos después (10:00:30), ingresa un cobro con la misma tarjeta en una tienda de electrónica en Madrid. A menos que Juan tenga una nave supersónica, es físicamente imposible: le clonaron la tarjeta. El sistema debe correlacionar ambas operaciones en la ventana de 120 segundos y bloquear la cuenta."*
>
> *"Con la **Ráfaga**: un atacante que vulnera una clave bancaria intenta realizar transferencias inmediatas de $10.000 cada 5 segundos para vaciar la cuenta antes de que la víctima reciba el SMS. El sistema detecta que al quinto intento en menos de un minuto ya se superó el límite permitido."*

### Contraste de Diseño
- **Se hizo así:** Se modeló la entidad `Transaccion` con timestamp numérico entero (`instante` en segundos de época) y campos inmutables.
- **Si se hubiera hecho de otra forma:** Si procesáramos las operaciones sin ordenamiento previo, no podríamos computar diferencias de tiempo continuas. Y si usáramos strings para representar fechas (ej. `"2026-09-11 10:00:00"`), el parseo de strings en cada ciclo consumiría órdenes de magnitud más tiempo de CPU que una resta de enteros.

### Código para Captura (Slide 1)
> **Ubicación:** [`modelos.py`](file:///home/franco/Repositories/PE/PE/parcial_1/modelos.py#L4-L20) y [`detectores.py`](file:///home/franco/Repositories/PE/PE/parcial_1/detectores.py#L15-L20)

```python
# modelos.py - Entidad inmutable ultraliviana con slots
@dataclass(frozen=True, slots=True)
class Transaccion:
    id: int
    usuario: str
    instante: int          # Timestamp en segundos (restas directas en O(1))
    monto: float
    comercio: str
    ubicacion: str

# detectores.py - Ventanas temporales y umbrales de fraude
VENTANA_RAFAGA = 60            # 60 segundos
MINIMO_RAFAGA = 5              # 5 operaciones en 60 s
VENTANA_REPETICION = 300       # 5 minutos (300 s)
MINIMO_REPETICIONES = 3        # 3 operaciones identicas
VENTANA_UBICACIONES = 120      # 2 minutos (120 s)
LIMITE_MONTO_FIJO = 1200.0     # Piso minimo estadistico
```

---

## Diapositiva 2: Diseño Inicial

### Fundamento Teórico y Académico
- **Arquitectura de componentes:**
  - `modelos.py`: Modelado formal del dominio (dataclasses con inmutabilidad y `slots`).
  - `generador.py`: Generador de datos sintéticos pseudoaleatorios reproducibles (`random.seed(42)`).
  - `algoritmos_ordenamiento.py`: Aislamiento de los algoritmos de ordenamiento.
  - `detectores.py`: Diferentes estrategias de detección para permitir testing comparativo con las mismas firmas.
  - `medicion.py` y `perfilado.py`: Infraestructura de benchmarking, profiling y métricas.
- **Implementación Inicial (`detectar_inicial`):**
  - Aplica un enfoque directo y no estructurado (*naive / brute-force*).
  - Ordena la lista global con **Burbuja**.
  - Mantiene una lista plana acumulativa `procesadas = []`.
  - En cada paso del bucle principal, ejecuta 4 filtrados lineales mediante *list comprehensions* recorriendo `procesadas` y `ordenadas`.
  - Recalcula el perfil del usuario (media y varianza) en cada transacción sin reutilización.

### Ejemplo Práctico en Lenguaje Natural
> *"Imaginen que tenemos una caja con 5.000 tickets de compra tirados en el piso. Para verificar el ticket #1 (de Juan), una persona levanta los 5.000 tickets del piso, busca cuáles eran de Juan, y calcula a mano con calculadora su promedio. Pasa al ticket #2 (que casualmente también es de Juan) y vuelve a levantar los 5.000 tickets del piso y vuelve a recalcular el promedio de Juan de nuevo. Para 5.000 tickets, termina levantando tickets del piso 25 millones de veces."*

### Contraste de Diseño
- **Se hizo así al inicio:** Para establecer una versión de referencia (*baseline*) cuya exactitud lógica esté garantizada y sirva para validar que las versiones optimizadas no introduzcan falsos positivos ni falsos negativos.
- **Si se hubiera dejado así:** Con 100 transacciones funciona en 0.002s, pero con 5.000 transacciones tarda 1.56s. Con 50.000 transacciones tardaría más de 2 minutos, haciendo inviable el sistema.

### Código para Captura (Slide 2)
> **Ubicación:** [`detectores.py`](file:///home/franco/Repositories/PE/PE/parcial_1/detectores.py#L94-L122)

```python
# detectores.py -> detectar_inicial()
def detectar_inicial(transacciones: list[Transaccion]) -> list[Alerta]:
    """Version inicial ingenua: O(n^2) en tiempo."""
    ordenadas = ordenar_burbuja(transacciones)  # Cuello de botella 1: Burbuja O(n^2)
    procesadas: list[Transaccion] = []
    alertas: list[Alerta] = []

    for transaccion in ordenadas:  # Bucle externo: n transacciones
        # Ineficiencia 1: Recorre toda la lista procesada O(n) para filtrar historial
        historial = [ant for ant in procesadas if ant.usuario == transaccion.usuario]
        
        # Ineficiencia 2: Recorre toda la lista global O(n) para buscar al usuario
        todas_usuario = [cand for cand in ordenadas if cand.usuario == transaccion.usuario]
        
        # Ineficiencia 3: Recalculo redundante de media y desviacion 5000 veces
        perfil = _calcular_perfil(todas_usuario)

        if transaccion.monto > perfil.limite_monto_alto:
            alertas.append(_crear_alerta(transaccion, "MONTO_ALTO", "..."))
            
        procesadas.append(transaccion)

    return _ordenar_alertas(alertas)
```

---

## Diapositiva 3: Complejidad Algorítmica

### Fundamento Teórico y Académico
- **Deducción Matemática de Burbuja:**
  - El algoritmo compara pares adyacentes $(x_i, x_{i+1})$. En la pasada $k$, realiza $n - k$ comparaciones.
  - Número total de comparaciones:
    $$\sum_{k=1}^{n-1} (n - k) = (n - 1) + (n - 2) + \dots + 1 = \frac{n(n - 1)}{2} = \frac{1}{2}n^2 - \frac{1}{2}n$$
  - Descartando términos de menor orden y coeficientes constantes: $\mathbf{O(n^2)}$ en tiempo para el caso peor y caso promedio.
- **Complejidad del Bucle de Detección:**
  - Para cada elemento $i \in [1, n]$, se realizan filtrados sobre arreglos de longitud proporcional a $n$:
    $$T(n) = \sum_{i=1}^n c \cdot i \approx c \frac{n(n + 1)}{2} \in \mathbf{O(n^2)}$$
- **Total Inicial:** $O(n^2) + O(n^2) = \mathbf{O(n^2)}$.
- **Impacto de Escalabilidad:**
  - Al duplicar el tamaño de entrada ($n \to 2n$), el trabajo computacional se multiplica por $(2)^2 = 4$.
  - Al multiplicar la entrada por 5 ($1.000 \to 5.000$), el trabajo teórico se multiplica por $5^2 = \mathbf{25\text{ veces}}$.

### Ejemplo Práctico en Lenguaje Natural
> *"Ordenar con Burbuja es como ordenar una baraja de 5.000 cartas en la mano comparando la carta 1 con la 2; si están desordenadas las cambiamos. Luego la 2 con la 3, la 3 con la 4... hasta el final. Y luego repetir esa pasada 5.000 veces. Realiza más de 12.500.000 comparaciones. Cualquier algoritmo cuadrático es el enemigo número uno de la escalabilidad."*

### Contraste de Diseño
- **Por qué mostramos Burbuja:** Para ilustrar que la elección del algoritmo equivocado destruye cualquier optimización posterior a nivel de microprocesador o hardware.
- **Qué observamos en las mediciones:** Con 1.000 transacciones tardó 0.09s; con 5.000 transacciones saltó a 1.65s (se multiplicó por casi 19 veces).

### Código para Captura (Slide 3)
> **Ubicación:** [`algoritmos_ordenamiento.py`](file:///home/franco/Repositories/PE/PE/parcial_1/algoritmos_ordenamiento.py#L8-L24)

```python
# algoritmos_ordenamiento.py -> ordenar_burbuja()
def ordenar_burbuja(transacciones: list[Transaccion]) -> list[Transaccion]:
    """Complejidad Temporal: O(n^2) en el peor y caso promedio."""
    resultado = transacciones.copy()
    cantidad = len(resultado)

    # Bucles anidados: n*(n-1)/2 comparaciones e intercambios
    for pasada in range(cantidad - 1):
        for posicion in range(cantidad - pasada - 1):
            actual = resultado[posicion]
            siguiente = resultado[posicion + 1]
            if actual.instante > siguiente.instante:
                # Intercambio in-place de elementos vecinos
                resultado[posicion], resultado[posicion + 1] = siguiente, actual

    return resultado
```

---

## Diapositiva 4: Algoritmos y Estructuras de Datos

### Fundamento Teórico y Académico
- **Selección de Quicksort ($O(n \log n)$):**
  - Aplica la técnica algorítmica de **Divide y Vencerás** (*Divide and Conquer*).
  - Particiona el conjunto en tres subarreglos: menores, iguales y mayores al pivote.
  - Selección de Pivote Central (`instante[len // 2]`): evita la degradación patológica a $O(n^2)$ que ocurre con el primer o último elemento en listas ya ordenadas o semiordenadas.
  - Recurrencia: $T(n) = 2T(n/2) + O(n) \implies \mathbf{O(n \log n)}$ promedio.
- **Estructuras de Datos Eficientes:**
  1. **`collections.deque` (Double-Ended Queue):**
     - En Python, `list` es un arreglo dinámico contiguo en memoria. Invocar `list.pop(0)` para descartar elementos viejos desplaza $k-1$ punteros en memoria RAM, con costo temporal $\mathbf{O(k)}$.
     - `deque` está implementada en C como una lista doblemente enlazada de bloques fijos de 64 elementos. Operaciones `append()` y `popleft()` son $\mathbf{O(1)}$ estricto por manipulación de punteros.
  2. **`dict` / `defaultdict`:**
     - Tablas hash con acceso, inserción y actualización en tiempo constante promedio $\mathbf{O(1)}$.
     - Se utilizan para indexar transacciones por usuario y llevar conteo de frecuencias de firmas `(monto, comercio)` y ciudades.
  3. **`set`:**
     - Conjunto hash con verificación de pertenencia `x in S` en $\mathbf{O(1)}$ para deduplicación de alertas.
  4. **Técnica de Ventana Deslizante (*Sliding Window*):**
     - Cada elemento del usuario entra a la cola una sola vez y sale una sola vez. El bucle de detección para las $m$ transacciones de un usuario pasa de $O(m^2)$ a **estrictamente lineal $\mathbf{O(m)}$**.

### Ejemplos Prácticos en Lenguaje Natural
1. **Quicksort:**
   > *"En vez de comparar carta por carta, Quicksort elige una carta de referencia del medio (el pivote) y divide la baraja en dos pilas: los que ocurrieron antes a la izquierda y los que ocurrieron después a la derecha. Luego repite lo mismo en cada pila. En lugar de hacer 12 millones de operaciones, resuelve el ordenamiento en apenas 60.000 operaciones."*
2. **`deque` vs `list` en la Ventana Deslizante:**
   > *"Imaginen la fila de un banco donde solo pueden permanecer quienes llegaron en los últimos 60 segundos. Entra una persona nueva por atrás (`append`). Si la primera persona de adelante llegó hace más de 60 segundos, sale de la fila.*
   >
   > *Si usamos una lista común (`list.pop(0)`), sacar a la persona de adelante obliga a empujar físicamente a las 99 personas que están atrás un casillero hacia adelante ($O(k)$ operaciones de memoria).*
   >
   > *Con una cola `deque` (`deque.popleft()`), sacar al primero es instantáneo ($O(1)$) porque solo desconecta un puntero sin mover a nadie."*
3. **`dict` y `set`:**
   > *"En vez de recorrer toda la lista preguntando: '¿está Juan en la posición 1?, ¿en la 2?, ¿en la 3?', el `dict` tiene un casillero directo con la etiqueta 'Juan' al que accedemos en fracciones de microsegundo en $O(1)$."*

### Contraste de Diseño
- **Se hizo así:** `Quicksort` + `deque` + `dict` + `set`.
- **Si se hubiera mantenido listas comunes:** Cada vez que una transacción vencía en la ventana temporal, el sistema desperdiciaba ciclos de CPU reacomodando memoria en el heap de Python.

### Código para Captura (Slide 4)
> **Ubicación:** [`algoritmos_ordenamiento.py`](file:///home/franco/Repositories/PE/PE/parcial_1/algoritmos_ordenamiento.py#L26-L45) y [`detectores.py`](file:///home/franco/Repositories/PE/PE/parcial_1/detectores.py#L190-L245)

```python
# 1. Quicksort con Divide y Venceras: O(n log n) promedio
def ordenar_quicksort(transacciones: list[Transaccion]) -> list[Transaccion]:
    if len(transacciones) <= 1:
        return transacciones.copy()
    pivote = transacciones[len(transacciones) // 2].instante  # Pivote central
    menores = [t for t in transacciones if t.instante < pivote]
    iguales = [t for t in transacciones if t.instante == pivote]
    mayores = [t for t in transacciones if t.instante > pivote]
    return ordenar_quicksort(menores) + iguales + ordenar_quicksort(mayores)

# 2. Ventanas deslizantes con deque O(1), dict O(1) y set O(1)
ventana_rafaga: deque[Transaccion] = deque()
emitidas: set[tuple[int, str]] = set()

for tx in grupo:
    # Desalojo O(1): elimina elementos vencidos sin mover memoria
    while ventana_rafaga and tx.instante - ventana_rafaga[0].instante > VENTANA_RAFAGA:
        ventana_rafaga.popleft()  # O(1) estricto (en list seria O(k))
    ventana_rafaga.append(tx)    # O(1)
    
    if len(ventana_rafaga) >= MINIMO_RAFAGA:
        clave = (tx.id, "RAFAGA")
        if clave not in emitidas:  # Verificacion O(1) en hash set
            emitidas.add(clave)
            alertas.append(_crear_alerta(tx, "RAFAGA", "..."))
```

---

## Diapositiva 5: Memoización y Caching

### Fundamento Teórico y Académico
- **Diferenciación conceptual formal:**
  - **Memoización:** Técnica de optimización determinística (típica de programación dinámica) que almacena los resultados de funciones puras referencialmente transparentes para no recomputarlos ante los mismos argumentos.
  - **Caching Inteligente:** Extiende la memoización incorporando **políticas de reemplazo de páginas/entradas (LRU)** con memoria acotada y **mecanismos explícitos de invalidación**.
- **Diseño de `CachePerfiles`:**
  - Almacena el `PerfilUsuario` (media, desviación y límite).
  - Utiliza `functools.lru_cache(maxsize=1024)`. Si el espacio se satura, la política LRU (*Least Recently Used*) desaloja automáticamente las entradas menos consultadas, evitando un crecimiento no acotado de memoria RAM (*Memory Leaks*).
  - **Invalidación de Caché:** El método `cargar()` incrementa un contador interno de versión y ejecuta `cache_clear()`. Esto garantiza que, al ingresar un lote nuevo de transacciones, no se sirvan datos viejos (*stale data*).
- **Métricas de Rendimiento Obtenidas:**
  - En 5.000 transacciones, se produjeron solo **101 cómputos reales (cache-misses)** y **4.899 accesos instantáneos (cache-hits)**. Ratio de acierto: **97.98%**.

### Ejemplo Práctico en Lenguaje Natural
> *"Imaginen que son cajeros y cada vez que viene Juan a pagar, tienen que pedirle las últimas 50 facturas de su vida, sumarlas todas y calcular su promedio con calculadora. Sería absurdo. Lo inteligente es calcularlo la primera vez, anotarlo en un post-it pegado al monitor (eso es memoización), y las siguientes 49 veces que vuelva Juan leemos el número directamente del post-it.*
>
> *¿Por qué pusimos un límite de 1.024 (`maxsize=1024`)? Porque si atendemos a 1 millón de clientes, se nos llena el monitor de post-its y nos quedamos sin espacio en la oficina (memoria RAM agotada). La política LRU tira a la basura el post-it del cliente que hace más tiempo no viene.*
>
> *¿Y la invalidación (`cache_clear()`)? Si mañana entra un nuevo archivo de transacciones del mes siguiente, rompemos los post-its viejos para no tomar decisiones con límites desactualizados."*

### Contraste de Diseño
- **Se hizo así:** `@lru_cache(maxsize=1024)` con método `cargar()` e invalidación explícita.
- **Si se hubiera usado un `dict` global infinito sin límite:** En un entorno bancario continuo con millones de usuarios, el proceso terminaría colapsando el servidor por consumo desmedido de memoria RAM (*OOM Killer*).
- **Si no se invalidara:** Un usuario que cambió su patrón de consumo seguiría siendo evaluado con su comportamiento del mes pasado.

### Código para Captura (Slide 5)
> **Ubicación:** [`detectores.py`](file:///home/franco/Repositories/PE/PE/parcial_1/detectores.py#L42-L68)

```python
# detectores.py -> CachePerfiles
class CachePerfiles:
    """Cache inteligente: memoizacion + politica LRU + invalidacion."""

    def __init__(self, capacidad: int = 1024) -> None:
        self._grupos: dict[str, list[Transaccion]] = {}
        self._version = 0
        # LRU Cache acotado a 1024 perfiles maximos
        self._calcular_memorizado = lru_cache(maxsize=capacidad)(self._calcular)

    def cargar(self, grupos: dict[str, list[Transaccion]]) -> None:
        """Invalida la cache al ingresar un nuevo lote (previene stale data)."""
        self._grupos = grupos
        self._version += 1
        self._calcular_memorizado.cache_clear()  # Limpieza explicita

    def obtener(self, usuario: str) -> PerfilUsuario:
        """Devuelve el perfil memorizado en O(1) o lo computa si hay cache-miss."""
        return self._calcular_memorizado(usuario, self._version)

    def estadisticas(self) -> tuple[int, int]:
        info = self._calcular_memorizado.cache_info()
        return info.hits, info.misses  # 4.899 aciertos vs solo 101 calculos
```

---

## Diapositiva 6: Concurrencia y Paralelismo

### Fundamento Teórico y Académico
- **Arquitectura de Particionado (Shared-Nothing):**
  - Dado que las 4 reglas de fraude son independientes por usuario, el dominio es naturalmente paralelizable (*embarrassingly parallel*).
  - Los usuarios se reparten en lotes disjuntos mediante balanceo *round-robin*. No existe memoria compartida ni se requieren cerrojos (*locks / mutex*), eliminando el riesgo de condiciones de carrera (*race conditions*) y bloqueos mutuos (*deadlocks*).
- **¿Por qué `ProcessPoolExecutor` y NO Hilos (`threading`)?:**
  - La carga de trabajo es intensiva en CPU (*CPU-bound*).
  - En CPython, el **GIL (Global Interpreter Lock)** es un mutex que protege las estructuras de memoria del intérprete, impidiendo que múltiples hilos ejecuten bytecode de Python simultáneamente en diferentes núcleos de CPU. Usar hilos en este escenario solo hubiera agregado sobrecarga de cambio de contexto sin paralelismo real.
  - `ProcessPoolExecutor` crea procesos independientes del sistema operativo con su propio espacio de memoria virtual y su propia instancia del intérprete, aprovechando núcleos físicos reales.
- **Análisis de Trade-off y Ley de Amdahl:**
  - La creación de procesos de SO, la serialización de objetos con `pickle` y la comunicación entre procesos mediante sockets/pipes UNIX (**IPC - Inter-Process Communication**) introduce un costo fijo base de $\approx 70\text{ a }100\text{ ms}$.
  - Como la versión secuencial optimizada resuelve el lote completo en solo **$17\text{ ms}$**, el costo de coordinación supera ampliamente la ganancia del paralelismo.

### Ejemplo Práctico en Lenguaje Natural
> *"Imaginen que tienen una tarea rápida en una oficina: revisar 5 páginas de texto. Una sola persona rápida y organizada (nuestra versión secuencial optimizada) lo lee en 17 segundos.*
>
> *Si decidimos 'paralelizar', contratamos a 4 empleados. Pero para darles trabajo tenemos que fotocopiar las páginas, meterlas en sobres, enviarlas por correo postal a 4 edificios distintos (eso es la serialización IPC / pickling de procesos), esperar a que abran los sobres, y luego esperar que nos devuelvan las cartas y consolidar las respuestas.*
>
> *El trámite burocrático de coordinar a los 4 empleados tardó 200 segundos. Como la tarea original era tan rápida, el costo administrativo superó ampliamente el beneficio. Eso en computación se llama **overhead de comunicación inter-proceso (IPC)**."*

### Contraste de Diseño
- **Decisión de Ingeniería:** Implementamos y medimos la versión paralela, pero **la descartamos formalmente para la versión final**.
- **Si hubiéramos asumido a ciegas que 'paralelo siempre es mejor':** Habríamos puesto en producción una solución que consume 15 veces más memoria RAM (1.17 MB vs 0.08 MB) y tarda 12 veces más tiempo (0.215 s vs 0.017 s). Demostramos criterio ingenieril al descartar una técnica cuando las métricas comprueban que no aporta valor neto.

### Código para Captura (Slide 6)
> **Ubicación:** [`detectores.py`](file:///home/franco/Repositories/PE/PE/parcial_1/detectores.py#L340-L368)

```python
# detectores.py -> detectar_paralelo()
def detectar_paralelo(transacciones: list[Transaccion], trabajadores: int | None = None):
    grupos = list(_agrupar_por_usuario(transacciones).items())
    cantidad_trabajadores = trabajadores or min(4, os.cpu_count() or 1)

    # Reparto de lotes balanceado sin estado compartido (Shared-Nothing)
    lotes = [[] for _ in range(cantidad_trabajadores)]
    for indice, grupo in enumerate(grupos):
        lotes[indice % cantidad_trabajadores].append(grupo)

    # ProcessPoolExecutor elude el GIL usando procesos reales
    with ProcessPoolExecutor(max_workers=cantidad_trabajadores) as ejecutor:
        # Sobrecarga: serializacion (pickle) y transmision IPC
        resultados = ejecutor.map(_procesar_lote, lotes)
        alertas = [alerta for res in resultados for alerta in res]

    return _ordenar_alertas(alertas)
```

---

## Diapositiva 7: Perfilado del Código

### Fundamento Teórico y Académico
- **Instrumentación Determinística:**
  - Se utilizó `cProfile`, un perfilador determinístico incorporado en la biblioteca estándar de Python que monitorea todos los eventos de llamada de función, retorno y excepción.
  - Métricas registradas con `pstats`:
    - `ncalls`: Número de invocaciones.
    - `tottime`: Tiempo total exclusivo consumido en la propia función (excluyendo subllamadas).
    - `cumtime`: Tiempo acumulado consumido en la función y todas sus subllamadas.
- **Diagnóstico Científico de Cuellos de Botella (*Bottlenecks*):**
  - **En la versión inicial:**
    - Tiempo total acumulado: $\sim 1.564\text{ s}$.
    - `ordenar_burbuja`: consumió **$0.812\text{ s}$ ($51.9\%$ del tiempo total)**.
    - Comprensiones de lista anidadas (`<listcomp>`): consumieron **$0.435\text{ s}$ ($27.8\%$)**.
    - El **$79.7\%$ del tiempo de CPU** estaba concentrado en solo esas dos operaciones.
  - **En la versión optimizada:**
    - El tiempo acumulado cayó a **$0.017\text{ s}$**, distribuido de manera equilibrada en microsegundos entre la generación de ventanas y el recorrido lineal.

### Ejemplo Práctico en Lenguaje Natural
> *"Optimizar código sin perfilar es como ir al médico con dolor de panza y que el cirujano te opere la rodilla por las dudas. `cProfile` es la radiografía médica del software: nos muestra exactamente cuántas veces se llamó a cada función y cuántos milisegundos consumió.*
>
> *Al correr el perfilado sobre la versión inicial, la radiografía fue contundente: de 1.56 segundos totales, **0.81 segundos se iban en `ordenar_burbuja`** y **0.43 segundos en las comprensiones de listas repetidas**. El 80% del problema estaba en solo dos lugares; supimos exactamente dónde intervenir sin perder tiempo en partes accesorias."*

### Contraste de Diseño
- **Se hizo así:** Perfilado guiado por datos con `cProfile.runcall()` y exportación a archivos `.prof` analizables con `pstats`.
- **Si hubiéramos optimizado por intuición:** Podríamos haber intentado optimizar las operaciones matemáticas de la varianza o el generador de datos, logrando mejoras imperceptibles porque esas funciones no representaban ni el 1% del cuello de botella.

### Código para Captura (Slide 7)
> **Ubicación:** [`perfilado.py`](file:///home/franco/Repositories/PE/PE/parcial_1/perfilado.py#L12-L28) y salida en consola

```python
# perfilado.py -> _perfilar()
def _perfilar(nombre: str, funcion, transacciones, carpeta: Path):
    perfilador = cProfile.Profile()
    alertas = perfilador.runcall(funcion, transacciones)

    # Exportacion binaria (.prof) y formateo de estadisticas acumuladas
    perfilador.dump_stats(carpeta / f"perfilado_{nombre}.prof")
    texto = io.StringIO()
    pstats.Stats(perfilador, stream=texto).sort_stats("cumulative").print_stats(15)
    return alertas, texto.getvalue()

# SALIDA REAL DEL PERFILADOR (Bottlenecks expuestos en la version inicial):
# ncalls  tottime  cumtime  filename:lineno(function)
#      1    0.001    1.564  detectores.py:94(detectar_inicial)
#      1    0.812    0.812  algoritmos_ordenamiento.py:8(ordenar_burbuja) <-- 51.9%
#   5000    0.435    0.435  detectores.py:101(<listcomp>)                 <-- 27.8%
```

---

## Diapositiva 8: Comparación de Resultados y Escalabilidad

### Fundamento Teórico y Académico
- **Metodología de Medición Rigurosa:**
  - **Medición de Tiempo:** Se utilizó `time.perf_counter()`, un reloj monotónico de hardware con la mayor resolución disponible en el sistema operativo, inmune a ajustes de reloj del sistema o sincronizaciones NTP.
  - **Medición de Memoria:** Se utilizó `tracemalloc`, que instrumenta los allocators de memoria de CPython a bajo nivel para capturar el pico máximo de memoria asignada en el heap (`get_traced_memory()[1]`).
  - *Limitación documentada:* En la versión paralela, `tracemalloc` solo mide el heap del proceso padre, no la memoria de los procesos hijos del sistema operativo.
- **Tabla Comparativa de las 5 Versiones (5.000 Transacciones):**

| Versión Evaluada | Tiempo Real (s) | Memoria RAM (MB) | Alertas Emitidas | Diagnóstico Técnico |
|---|---:|---:|:---:|---|
| **1. Implementación inicial** | **1.5639 s** | 0.08 MB | 9 | Cuello de botella en Burbuja y búsquedas repetidas $O(n^2)$ |
| **2. Estructura optimizada** | **0.0745 s** | 0.06 MB | 9 | Salto de 21x gracias al desacople con `dict`, `deque` y `set` |
| **3. Algoritmo optimizado** | **0.0178 s** | 0.08 MB | 9 | Quicksort $O(n \log n)$ + Cache LRU: **aceleración de ~90x** |
| **4. Concurrencia/paralelismo** | **0.2150 s** | 1.17 MB | 9 | Descartada: Sobrecarga de IPC y creación de procesos |
| **5. Versión final** | **0.0178 s** | 0.08 MB | 9 | **Secuencial Optimizada: Elección Definitiva Justificada** |

- **Análisis de Escalabilidad:**
  - A 1.000 transacciones: Inicial 0.092 s vs Optimizada 0.0014 s ($\mathbf{65.3\times}$ de mejora).
  - A 2.500 transacciones: Inicial 0.283 s vs Optimizada 0.0036 s ($\mathbf{78.1\times}$ de mejora).
  - A 5.000 transacciones: Inicial 1.653 s vs Optimizada 0.0070 s ($\mathbf{235.1\times}$ de mejora).
  - La brecha no es lineal, se amplía a favor de la versión optimizada a medida que aumenta $n$, confirmando empíricamente la diferencia asintótica entre $O(n^2)$ y $O(n \log n)$.

### Ejemplo Práctico en Lenguaje Natural
> *"Miren cómo cambia la historia cuando aumentamos el volumen:*
> - *Con 1.000 transacciones la inicial tardaba 0.09s y la optimizada 0.0014s (mejora de 65x).*
> - *Con 5.000 transacciones la inicial saltó a 1.65 segundos, mientras que la optimizada apenas subió a 0.007 segundos. **¡La mejora saltó a 235 veces!***
>
> *¿Qué significa esto en un evento masivo como un **CyberMonday** con 100.000 transacciones?*
> - *La versión inicial tardaría **más de 1 hora** de reloj (el servidor colapsa y las compras se caen).*
> - *Nuestra versión optimizada procesa las 100.000 transacciones en **menos de medio segundo**."*

### 📸 Código y Gráficos para la Diapositiva (Slide 8)
> **Ubicación:** [`medicion.py`](file:///home/franco/Repositories/PE/PE/parcial_1/medicion.py#L40-L59) y datos de [`comparacion.csv`](file:///home/franco/Repositories/PE/PE/parcial_1/resultados/comparacion.csv)

```python
# medicion.py -> _medir()
def _medir(version: str, funcion, transacciones, observacion: str):
    tracemalloc.start()
    inicio = time.perf_counter()
    alertas = funcion(transacciones)
    tiempo = time.perf_counter() - inicio
    _, memoria_pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return ResultadoMedicion(version, tiempo, memoria_pico / (1024 * 1024), len(alertas))
```

*(Incluir en la diapositiva las dos imágenes generadas en alta resolución: `resultados/comparacion_tiempos.png` y `resultados/escalabilidad.png`).*

---

## 🎯 Frase de Cierre para Ganarte al Profesor (15 segundos)

> *"En conclusión, optimizar no es agregar complejidad porque sí. Demostramos que la mayor ganancia de rendimiento provino de la teoría clásica de ciencias de la computación: elegir las estructuras de datos adecuadas (`deque` y `dict`), un algoritmo de ordenamiento eficiente (`Quicksort`) y memoización inteligente. Y demostramos criterio ingenieril al descartar el paralelismo porque nuestras mediciones empíricas comprobaron que agregaba sobrecarga innecesaria."*
