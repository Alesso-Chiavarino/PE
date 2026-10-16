# Informe tecnico - Detector de transacciones sospechosas

Este documento explica como el programa cumple cada punto del enunciado. Los
tiempos son los obtenidos en la computadora de desarrollo con 5.000
transacciones y pueden variar ligeramente entre ejecuciones.

## 1. Implementacion inicial

El sistema recibe transacciones desordenadas y detecta cuatro situaciones:

- un monto muy superior al comportamiento habitual del usuario;
- cinco o mas operaciones dentro de 60 segundos;
- tres operaciones iguales dentro de cinco minutos;
- operaciones cercanas desde ubicaciones diferentes.

La funcion `detectar_inicial` de `detectores.py` es la baseline. Primero ordena
con Burbuja y despues, para cada transaccion, vuelve a recorrer el historial y
las transacciones del usuario. Es funcional y sirve como punto de comparacion,
pero hace trabajo repetido.

La arquitectura se separa en archivos sencillos:

| Archivo | Responsabilidad |
|---|---|
| `modelos.py` | Datos de transacciones, alertas y perfiles |
| `generador.py` | Datos de prueba repetibles |
| `algoritmos_ordenamiento.py` | Burbuja y Quicksort |
| `detectores.py` | Las distintas versiones del detector |
| `medicion.py` | Tiempo, memoria, tablas y graficos |
| `perfilado.py` | Comparacion con `cProfile` |
| `interfaz/ventana.py` | Interfaz grafica nativa con Tkinter |

## 2. Analisis de complejidad

### Ordenamiento Burbuja

Burbuja compara elementos vecinos. En la primera pasada realiza `n - 1`
comparaciones, despues `n - 2`, y continua hasta una comparacion:

```text
(n - 1) + (n - 2) + ... + 1 = n(n - 1) / 2
```

Al eliminar constantes y terminos menores queda **O(n^2)**. Si la cantidad de
datos se duplica, el trabajo puede acercarse a cuatro veces. Es relevante
porque las transacciones llegan desordenadas y deben ordenarse por tiempo antes
de aplicar las ventanas temporales.

### Ordenamiento Quicksort

Quicksort elige un pivote y divide los datos en menores, iguales y mayores. En
un caso promedio hay aproximadamente `log2(n)` niveles y en cada nivel se
revisan `n` elementos. Por eso el costo promedio es **O(n log n)**. Su peor caso
es O(n^2), aunque elegir como pivote el valor central reduce ese riesgo para los
datos de este proyecto.

### Busquedas y ventanas

La version inicial hace busquedas lineales O(n) dentro de un ciclo que se
ejecuta n veces; por eso esta parte tambien llega a **O(n^2)**. La version
optimizada agrupa una vez con un diccionario en O(n) promedio. Luego cada
transaccion entra y sale una sola vez de cada `deque`, tambien O(n) en total.
Como el ordenamiento domina, la version optimizada queda en **O(n log n)**
promedio.

## 3. Eleccion de algoritmo

Se comparan dos algoritmos vistos en clase: Burbuja y Quicksort. Se eligio
Quicksort para la version optimizada porque mantiene el codigo entendible y su
O(n log n) promedio escala mucho mejor que el O(n^2) de Burbuja. Ambos producen
exactamente el mismo orden y las mismas alertas, lo cual esta comprobado por los
tests.

Una busqueda binaria no resolveria la operacion principal: el detector no busca
un unico valor, sino que debe recorrer todas las operaciones y mantener varias
ventanas de tiempo. Para este caso, Quicksort mas ventanas deslizantes resulta
mas adecuado.

## 4. Estructuras de datos

- **Lista:** almacena la entrada y las alertas. Recorrerla cuesta O(n) y agregar
  al final cuesta O(1) amortizado.
- **Diccionario (`dict`):** agrupa por usuario y cuenta firmas y ubicaciones.
  Buscar, agregar o actualizar cuesta O(1) promedio.
- **Cola de doble extremo (`deque`):** representa cada ventana temporal. Agregar
  al final y quitar el dato mas antiguo cuestan O(1). Quitar el primer elemento
  de una lista costaria O(n) por los desplazamientos.
- **Conjunto (`set`):** registra las alertas ya emitidas y evita duplicados con
  consulta O(1) promedio.

## 5. Memoizacion y caching inteligente

`CachePerfiles` almacena el promedio, la desviacion y el limite de monto alto de
cada usuario. Conviene almacenarlos porque el perfil no cambia durante un mismo
analisis y es consultado para cada transaccion del usuario.

Se reutiliza el perfil cuando otra transaccion pertenece al mismo usuario. El
cache usa `lru_cache` y conserva como maximo 1.024 perfiles. Al cargar un nuevo
conjunto de transacciones incrementa su version y ejecuta `cache_clear()`, por
lo que nunca devuelve perfiles calculados con datos anteriores.

**Memoizacion** significa guardar el resultado de un calculo para las mismas
entradas. **Caching** es un concepto mas amplio que tambien define capacidad,
reutilizacion e invalidacion. Esta implementacion hace memoizacion del calculo
y agrega una politica de cache LRU e invalidacion.

Con 5.000 transacciones hubo 101 calculos reales y 4.899 aciertos de cache. En
la baseline el perfil se calculaba 5.000 veces.

## 6. Concurrencia y paralelismo

`detectar_paralelo` usa `ProcessPoolExecutor`. Cada proceso recibe uno o mas
usuarios porque el resultado de un usuario no depende de otro. No hay escrituras
compartidas: el proceso principal combina y ordena las alertas al final, lo que
evita condiciones de carrera.

Se eligieron procesos y no `threading` porque la deteccion es trabajo de CPU y
el GIL de Python limita la ejecucion paralela de codigo Python en hilos. En un
caso ideal, el trabajo puede aproximarse a O((n log n) / p), donde `p` es la
cantidad de procesos.

El costo es crear procesos, serializar datos y mantener memoria separada. Para
5.000 transacciones, dos procesos tardaron 0,0797 s y la secuencial optimizada
0,0125 s. Por eso la version final conserva el paralelismo como experimento,
pero elige la secuencial optimizada: medir tambien permite descartar una
optimizacion que no conviene.

## 7. Perfilado y medicion

Se usan tres herramientas de la biblioteca estandar:

- `time.perf_counter()` mide tiempo con alta precision;
- `tracemalloc` mide el pico de memoria Python;
- `cProfile` identifica las funciones con mayor tiempo acumulado.

El perfilado de 5.000 transacciones mostro 0,809 s para la version inicial y
0,013 s para la optimizada. El principal cuello de botella individual fue
`ordenar_burbuja`, con 0,411 s. La mejora consistio en cambiar el ordenamiento,
evitar busquedas repetidas y reutilizar los perfiles.

### Comparacion obligatoria

| Version | Tiempo | Memoria | Observacion |
|---|---:|---:|---|
| Implementacion inicial | 0,9273 s | 0,08 MB | Baseline: Burbuja y busquedas repetidas |
| Estructura optimizada | 0,0530 s | 0,06 MB | Mejora de busqueda con `dict`, `deque` y `set` |
| Algoritmo optimizado | 0,0125 s | 0,08 MB | Quicksort y cache: mejor escalabilidad |
| Concurrencia/paralelismo | 0,0797 s | 1,17 MB | Dos procesos; se observa overhead |
| Version final | 0,0104 s | 0,08 MB | Secuencial optimizada: menor tiempo medido |

`tracemalloc` solo observa directamente el proceso principal, por lo que la
fila paralela no incluye toda la memoria interna de los procesos hijos. Esa es
una limitacion de la medicion que debe mencionarse.

### Escalabilidad

| Transacciones | Inicial | Optimizada | Mejora |
|---:|---:|---:|---:|
| 1.000 | 0,0361 s | 0,0011 s | 32,6 veces |
| 2.500 | 0,2053 s | 0,0027 s | 74,8 veces |
| 5.000 | 0,7920 s | 0,0051 s | 155,6 veces |

La distancia aumenta con el volumen, como predicen O(n^2) y O(n log n). Los
archivos CSV, los graficos y los perfiles completos quedan en `resultados/`.

## Ejecucion para la demostracion

```bash
cd parcial_2
source .venv/bin/activate
python main.py interfaz
```

En la ventana, **Analizar** ejecuta la version final y muestra las alertas.
**Comparar versiones** genera las cinco mediciones exigidas. Para repetir toda
la evidencia desde la consola:

```bash
python main.py benchmark --transacciones 5000 --trabajadores 2
python main.py perfilado --transacciones 5000
python main.py escalabilidad --volumenes 1000 2500 5000
python -m unittest discover -v
```

## Conclusion

La mayor mejora provino de reemplazar Burbuja y los recorridos repetidos por
Quicksort, diccionarios y ventanas deslizantes, junto con la reutilizacion de
perfiles. El paralelismo no mejoro este caso porque sus tareas son demasiado
cortas frente al costo de crear y comunicar procesos. Con mas trabajo por
usuario se podria volver a medir, pero no se debe asumir que mas procesos
siempre significan menor tiempo.
