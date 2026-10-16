# Justificacion del proyecto

## Detector de transacciones sospechosas

Este documento explica como el programa cumple los requisitos del primer
parcial. Los tiempos indicados se obtuvieron en la computadora de desarrollo
con 5.000 transacciones. Pueden variar ligeramente entre ejecuciones.

## 1. Implementacion inicial

La primera implementacion funcional es la **baseline** o linea base. Su
objetivo es resolver correctamente el problema antes de aplicar mejoras y
servir como referencia para las mediciones posteriores.

La funcion `detectar_inicial` de `detectores.py` recibe transacciones
desordenadas y detecta cuatro tipos de situaciones sospechosas:

- un monto muy superior al comportamiento habitual del usuario;
- cinco o mas operaciones dentro de 60 segundos;
- tres operaciones iguales dentro de cinco minutos;
- operaciones cercanas desde ubicaciones diferentes.

La baseline ordena las transacciones con el algoritmo Burbuja. Luego, para
cada transaccion, vuelve a recorrer las operaciones y el historial del
usuario. Es una solucion sencilla, entendible y funcional, pero repite trabajo
y pierde rendimiento al aumentar la cantidad de datos.

Se usa Burbuja de forma intencional en esta version. No se eligio porque sea el
mejor algoritmo, sino porque permite mostrar claramente el punto de partida y
compararlo con una alternativa mas eficiente.

La arquitectura se divide en archivos con responsabilidades simples:

| Archivo | Responsabilidad |
|---|---|
| `modelos.py` | Representa transacciones, alertas y perfiles |
| `generador.py` | Genera datos de prueba repetibles |
| `algoritmos_ordenamiento.py` | Implementa Burbuja y Quicksort |
| `detectores.py` | Contiene las diferentes versiones del detector |
| `medicion.py` | Mide tiempo y memoria y genera resultados |
| `perfilado.py` | Realiza el perfilado con `cProfile` |
| `interfaz/ventana.py` | Implementa la interfaz grafica con Tkinter |

**Explicacion oral breve:** la implementacion inicial es una solucion que ya
funciona y detecta las alertas, pero todavia no esta optimizada. La usamos como
baseline para medir de manera objetiva si las mejoras realmente sirven.

## 2. Analisis de complejidad

### Algoritmo Burbuja

Burbuja compara elementos vecinos y los intercambia cuando estan en el orden
incorrecto. En la primera pasada realiza `n - 1` comparaciones, en la segunda
`n - 2`, y continua hasta llegar a una comparacion:

```text
(n - 1) + (n - 2) + ... + 1 = n(n - 1) / 2
```

Al desarrollar la expresion aparece un termino `n^2`. En notacion Big O se
eliminan las constantes y los terminos menores, por lo que la complejidad es
**O(n^2)**.

Esto es relevante porque, si se duplica la cantidad de transacciones, el
trabajo puede acercarse a cuatro veces. Las transacciones necesitan estar
ordenadas cronologicamente para aplicar correctamente las ventanas de 60
segundos, dos minutos y cinco minutos.

### Algoritmo Quicksort

Quicksort selecciona un pivote y divide los elementos en tres grupos: menores,
iguales y mayores. En un caso promedio se forman aproximadamente `log2(n)`
niveles de division, y en cada nivel se procesan en total `n` elementos:

```text
n elementos x log2(n) niveles = O(n log n)
```

Su complejidad promedio es **O(n log n)** y su peor caso es **O(n^2)**. En esta
implementacion se toma el elemento central como pivote, lo que reduce el riesgo
de obtener divisiones muy desequilibradas con los datos utilizados.

### Busquedas y ventanas temporales

La version inicial realiza busquedas lineales **O(n)** dentro de un ciclo que
se ejecuta `n` veces. Por eso esta parte puede alcanzar **O(n^2)**.

La version optimizada agrupa las transacciones una sola vez con un diccionario,
lo que cuesta **O(n)** en promedio. Despues, cada transaccion entra y sale una
sola vez de las colas de las ventanas temporales, por lo que ese procesamiento
tambien es **O(n)** en total.

Como Quicksort es la operacion dominante, la complejidad promedio de la version
optimizada es **O(n log n)**.

**Explicacion oral breve:** Burbuja hace aproximadamente `n^2` comparaciones,
mientras que Quicksort divide el problema y necesita aproximadamente
`n log n` operaciones. Esta diferencia se vuelve importante cuando aumenta la
cantidad de transacciones.

## 3. Eleccion de algoritmo

Se comparan dos algoritmos sencillos vistos en clase:

- **Burbuja:** facil de comprender, pero con complejidad O(n^2).
- **Quicksort:** utiliza division por pivote y tiene complejidad O(n log n) en
  promedio.

Se reemplazo Burbuja por Quicksort en la version optimizada porque las
transacciones deben ordenarse por fecha y Quicksort presenta una mejor
escalabilidad. Ambos algoritmos producen el mismo orden y las mismas alertas,
algo que tambien se comprueba mediante los tests.

No se eligio busqueda binaria porque el programa no necesita encontrar un solo
elemento. El detector debe recorrer todas las operaciones para evaluar montos,
repeticiones, rafagas y ubicaciones. Por eso, para este problema resulta mas
apropiado combinar Quicksort con ventanas deslizantes.

**Explicacion oral breve:** la decision principal fue reemplazar Burbuja por
Quicksort. Los dos resuelven el mismo ordenamiento, pero Quicksort crece mucho
mas lentamente cuando aumenta el volumen de datos.

## 4. Estructuras de datos

### Lista

Las listas almacenan las transacciones de entrada, los grupos de operaciones y
las alertas obtenidas. Son adecuadas porque permiten recorrer los elementos en
orden en **O(n)** y agregar al final en **O(1) amortizado**.

### Diccionario (`dict`)

El diccionario agrupa las transacciones por identificador de usuario. Tambien
se utiliza para contar firmas de operaciones y ubicaciones.

Buscar, insertar o actualizar una clave cuesta **O(1) promedio**. De esta forma
se evita recorrer la lista completa cada vez que se necesitan las operaciones
de un usuario.

### Cola de doble extremo (`deque`)

Las colas `deque` representan las ventanas temporales. Las operaciones nuevas
se agregan al final y las antiguas se eliminan desde el principio.

Tanto `append` como `popleft` cuestan **O(1)**. Si se utilizara una lista y se
eliminara el primer elemento, los elementos restantes tendrian que desplazarse
y la operacion costaria **O(n)**.

### Conjunto (`set`)

El conjunto registra combinaciones de transaccion y tipo de alerta ya emitidas.
Permite comprobar en **O(1) promedio** si una alerta ya fue generada y evita
mostrar duplicados.

**Explicacion oral breve:** usamos diccionarios para acceder rapidamente a las
operaciones de cada usuario, `deque` para agregar y quitar elementos de las
ventanas en tiempo constante, listas para conservar los resultados y un `set`
para evitar alertas duplicadas.

## 5. Memoizacion y caching inteligente

La clase `CachePerfiles` de `detectores.py` guarda el perfil estadistico
calculado para cada usuario. El perfil contiene:

- promedio de los montos;
- desviacion estandar;
- limite utilizado para detectar un monto alto.

La clave conceptual del cache es:

```text
(usuario, version de los datos) -> perfil calculado
```

Conviene guardarlo porque el perfil de un usuario se consulta para cada una de
sus transacciones, pero no cambia durante una misma ejecucion. La primera
consulta realiza el calculo y las siguientes reutilizan el resultado.

La implementacion utiliza:

```python
@lru_cache(maxsize=1024)
```

El limite evita que la cache crezca sin control. Cuando se carga un conjunto
nuevo de transacciones, el programa incrementa la version y ejecuta
`cache_clear()`. Esto invalida los resultados anteriores y evita devolver
informacion obsoleta.

La **memoizacion** consiste en guardar el resultado de un calculo para
reutilizarlo cuando se repiten las mismas entradas. El **caching** es un
concepto mas amplio que tambien incluye una politica de capacidad,
reutilizacion e invalidacion. En este proyecto se memoiza el calculo del perfil
y se administra mediante una cache LRU con invalidacion.

Con 5.000 transacciones se obtuvieron aproximadamente:

- 101 calculos reales o fallos de cache;
- 4.899 reutilizaciones o aciertos de cache.

En la baseline el perfil se calculaba nuevamente para cada transaccion.

**Explicacion oral breve:** guardamos el perfil estadistico de cada usuario
porque se consulta muchas veces sin cambiar. Cuando llegan datos nuevos,
limpiamos la cache para no reutilizar informacion vieja.

## 6. Concurrencia y paralelismo

La funcion `detectar_paralelo` agrupa las transacciones por usuario y utiliza
`ProcessPoolExecutor` para analizar grupos de usuarios en procesos distintos.

Esto posee una justificacion tecnica: las alertas de un usuario solo dependen
de las transacciones de ese mismo usuario. Mientras un proceso analiza a
`USR-0001`, otro puede analizar a `USR-0002` sin compartir informacion.

Se eligieron procesos en lugar de `threading` porque el detector realiza
principalmente trabajo de CPU, como ordenamientos, comparaciones y calculos.
El GIL de Python limita la ejecucion paralela de codigo Python en varios hilos,
mientras que los procesos poseen interpretes separados y pueden utilizar
varios nucleos.

Cada proceso produce su propia lista de alertas. El proceso principal las
reune y las ordena al terminar. Como no se modifica una lista global desde
varios procesos, se evitan condiciones de carrera.

El paralelismo tambien introduce costos:

- creacion y finalizacion de procesos;
- serializacion y transferencia de datos;
- mayor consumo de memoria;
- necesidad de combinar los resultados.

Con 5.000 transacciones se midieron aproximadamente estos resultados:

| Version | Tiempo | Memoria medida |
|---|---:|---:|
| Optimizada secuencial | 0,0125 s | 0,08 MB |
| Paralela con dos procesos | 0,0797 s | 1,17 MB |

La version paralela fue mas rapida que la baseline, pero mas lenta que la
secuencial optimizada. Para este volumen, el trabajo de cada grupo es demasiado
corto y el overhead de los procesos supera el beneficio. Por eso la version
final utiliza la estrategia secuencial optimizada.

El paralelismo se conserva para demostrar la tecnica y su trade-off. Con un
volumen mucho mayor o un analisis mas costoso por usuario podria resultar
conveniente, pero seria necesario volver a medirlo.

**Explicacion oral breve:** los usuarios pueden analizarse en paralelo porque
son independientes. Usamos procesos para aprovechar varios nucleos, pero la
medicion mostro que, con 5.000 transacciones, crear y comunicar los procesos
cuesta mas que el tiempo ahorrado.

## 7. Perfilado y medicion

El proyecto utiliza herramientas incluidas en Python:

- `cProfile` identifica las funciones que consumen mas tiempo;
- `time.perf_counter()` mide el tiempo total con alta precision;
- `tracemalloc` mide el pico de memoria utilizado por Python.

No es necesario utilizar todas las herramientas mencionadas en el enunciado.
`cProfile` es la herramienta de perfilado elegida, mientras que
`perf_counter` y `tracemalloc` complementan el analisis con mediciones de
tiempo y memoria.

### Diferencia entre perfilado y medicion

La **medicion** indica cuanto tarda una version y cuanta memoria consume. El
**perfilado** muestra en que funciones se empleo ese tiempo y ayuda a localizar
el cuello de botella.

### Principal cuello de botella

`cProfile` mostro que la implementacion inicial tardo aproximadamente
`0,809 s`, mientras que `ordenar_burbuja` consumio por si sola cerca de
`0,411 s`. Por lo tanto, el ordenamiento Burbuja fue el principal cuello de
botella individual.

Para 5.000 transacciones, Burbuja puede realizar aproximadamente:

```text
5000 x 4999 / 2 = 12.497.500 comparaciones
```

Tambien se detecto trabajo repetido al buscar varias veces las transacciones de
un usuario y volver a calcular su perfil estadistico.

### Optimizaciones realizadas

1. Se agruparon las transacciones por usuario con un diccionario.
2. Se utilizaron `deque` para las ventanas temporales.
3. Se utilizo un `set` para evitar alertas duplicadas.
4. Se reemplazo Burbuja por Quicksort.
5. Se agrego la cache de perfiles.
6. Se evaluo una version paralela por usuario.

### Comparacion obligatoria

| Version | Tiempo | Memoria | Observacion |
|---|---:|---:|---|
| Implementacion inicial | 0,9273 s | 0,08 MB | Baseline con Burbuja y busquedas repetidas |
| Estructura optimizada | 0,0530 s | 0,06 MB | Mejora con `dict`, `deque` y `set` |
| Algoritmo optimizado | 0,0125 s | 0,08 MB | Quicksort y cache |
| Concurrencia/paralelismo | 0,0797 s | 1,17 MB | Dos procesos; se observa overhead |
| Version final | 0,0104 s | 0,08 MB | Secuencial optimizada |

Todas las versiones encontraron las mismas nueve alertas. Esto es importante
porque demuestra que las optimizaciones mejoraron el rendimiento sin cambiar
el resultado funcional.

`tracemalloc` mide directamente la memoria del proceso principal. Por eso el
valor de la version paralela no representa necesariamente toda la memoria
interna utilizada por los procesos hijos. Esta limitacion debe mencionarse al
presentar los resultados.

### Impacto de las mejoras

Al comparar el tiempo de la baseline con el de la version final:

```text
0,9273 / 0,0104 = aproximadamente 89 veces mas rapida
```

El valor exacto puede cambiar entre ejecuciones, pero la diferencia general se
mantiene.

### Escalabilidad

| Transacciones | Inicial | Optimizada | Mejora aproximada |
|---:|---:|---:|---:|
| 1.000 | 0,0361 s | 0,0011 s | 32,6 veces |
| 2.500 | 0,2053 s | 0,0027 s | 74,8 veces |
| 5.000 | 0,7920 s | 0,0051 s | 155,6 veces |

La mejora se mantiene y aumenta al crecer el volumen. Esto coincide con el
analisis teorico: la baseline crece como O(n^2), mientras que la version
optimizada crece como O(n log n) en promedio.

### Trade-offs

- Las estructuras optimizadas utilizan algo de memoria adicional para guardar
  diccionarios, colas, conjuntos y perfiles.
- La cache necesita una politica de limite e invalidacion.
- Quicksort es un poco mas complejo de explicar que Burbuja.
- El paralelismo agrega complejidad, transferencia de datos y memoria, y no
  siempre reduce el tiempo.

La conclusion mas importante es que una optimizacion debe conservar el
resultado correcto y demostrar su beneficio mediante mediciones. No alcanza
con agregar una tecnica suponiendo que sera mas rapida.

**Explicacion oral breve:** `cProfile` permitio encontrar que Burbuja era el
principal cuello de botella. Luego medimos tiempo y memoria en cada version.
La version final fue aproximadamente 89 veces mas rapida que la baseline con
5.000 transacciones. La mejora aumento con el volumen, mientras que el
paralelismo no fue conveniente por su overhead.

## Ejecucion de la demostracion

Para abrir la interfaz grafica:

```bash
cd parcial_2
source .venv/bin/activate
python main.py interfaz
```

En la ventana, **Analizar** ejecuta el detector final y muestra las alertas.
**Comparar versiones** ejecuta las cinco variantes y muestra su tiempo y
memoria.

Para generar nuevamente las mediciones desde la consola:

```bash
python main.py benchmark --transacciones 5000 --trabajadores 2
python main.py perfilado --transacciones 5000
python main.py escalabilidad --volumenes 1000 2500 5000
python -m unittest discover -v
```

## Conclusion general

La mayor mejora se obtuvo al reemplazar el ordenamiento Burbuja y los
recorridos repetidos por Quicksort, diccionarios y ventanas deslizantes. La
cache evito recalcular perfiles sin necesidad. El paralelismo fue implementado
y medido correctamente, pero no fue elegido para la version final porque su
overhead lo hizo mas lento para el volumen de la demostracion.

El proyecto muestra que la eleccion de algoritmos y estructuras de datos suele
tener mas impacto que agregar procesos sin medir. Todas las decisiones fueron
comparadas usando el mismo conjunto de transacciones para conservar una prueba
justa.
