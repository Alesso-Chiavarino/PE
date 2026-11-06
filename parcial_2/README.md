# Tercer parcial - Programación Eficiente

Sistema en Python que simula transacciones y detecta cuatro comportamientos
sospechosos:

- montos inusualmente altos;
- muchas operaciones en poco tiempo;
- operaciones iguales repetidas;
- actividad casi simultanea desde ubicaciones diferentes.

La tercera versión conserva las mejoras del segundo parcial y agrega integración
continua, controles automáticos de calidad y seguridad, políticas de aprobación,
reportes reproducibles y documentación técnica centralizada con Sphinx.

## Qué agrega el tercer parcial

- GitHub Actions ante cada push y pull request;
- Ruff y mypy para calidad estática y contratos de tipos;
- Radon con límites de complejidad;
- pytest y cobertura mínima del 90 por ciento;
- Bandit, pip-audit y detect-secrets para seguridad;
- benchmark relativo, profiling de CPU y límite de memoria;
- construcción y validación automática de la documentación Sphinx;
- artefactos JSON, XML, HTML y archivos de profiling descargables.

## Como ejecutarlo

El proyecto usa Python 3.10 o posterior. Las dependencias de desarrollo se
instalan dentro de un entorno virtual.

```bash
cd parcial_2
source .venv/bin/activate
python main.py demo --transacciones 5000
python main.py interfaz
python main.py benchmark --transacciones 5000 --trabajadores 2
python main.py perfilado --transacciones 5000
python main.py escalabilidad --volumenes 1000 2500 5000
python main.py generar-archivo --transacciones 100000 --salida datos/transacciones.csv
python main.py analizar-archivo datos/transacciones.csv --lote 10000
python -m pytest
```

La cantidad se puede cambiar en los comandos `demo`, `benchmark`, `perfilado`
y `generar-archivo` mediante `--transacciones`.

## Controles del tercer parcial

Los mismos controles del pipeline se pueden ejecutar localmente:

```bash
python -m ruff check .
python -m mypy algoritmos_ordenamiento.py archivos.py configuracion.py \
  detectores.py generador.py main.py medicion.py modelos.py monitoreo.py \
  perfilado.py interfaz tests scripts
python -m scripts.verificar_complejidad
python -m pytest --cov --cov-fail-under=90
python -m bandit -r . -x ./.venv,./tests,./docs,./presentacion,./resultados -ll
python -m pip_audit -r requirements.txt --cache-dir reportes/.pip-audit-cache
detect-secrets scan --all-files --baseline .secrets.baseline
python -m sphinx -W --keep-going -b html docs docs/_build/html
python -m scripts.verificar_rendimiento
python -m scripts.verificar_memoria
```

Los criterios de rechazo y la resolución de fallos están documentados en
`docs/mantenimiento.rst`. Los reportes se generan dentro de `reportes/` y el CI
los publica como artefactos de GitHub Actions.

## Herramientas heredadas del segundo parcial

Se eligieron herramientas presentes en el material de clase y simples de
ejecutar:

```bash
python -m pip install -r requirements-lock.txt
python -m pytest --cov=archivos --cov=configuracion --cov=detectores \
  --cov=generador --cov=algoritmos_ordenamiento --cov-report=term-missing
python -m ruff check .
python main.py perfilado --transacciones 5000
python -m snakeviz resultados/perfilado_optimizado.prof
python -m sphinx -b html docs docs/_build/html
```

`pytest` es el framework utilizado por las pruebas. SnakeViz aprovecha los
archivos `.prof` que el proyecto ya producia con `cProfile`, por lo que no exige
instrumentar nuevamente el programa. `psutil` registra memoria RSS, tiempo de
CPU y E/S cuando se procesa un archivo grande.

El detalle de las modificaciones se encuentra en `CAMBIOS_PARCIAL_2.md`.

La interfaz abre una ventana nativa con Tkinter para mostrar las alertas y la
comparacion de rendimiento. Todo su codigo esta separado en `interfaz/` y no
forma parte de los algoritmos de deteccion.

En macOS, si Python fue instalado con Homebrew y Tkinter no esta disponible:

```bash
brew install python-tk@3.14
```

`matplotlib` es opcional y solamente se usa para crear el grafico del benchmark:

```bash
python -m pip install -r requirements.txt
```

## Versiones comparadas

| Version | Idea principal | Complejidad temporal |
|---|---|---|
| Inicial | Ordena con Burbuja y recorre nuevamente las listas | O(n^2) |
| Estructuras optimizadas | Agrupa con `dict`, usa `deque` y mantiene Burbuja | O(n + suma de m^2) |
| Algoritmo + cache | Quicksort, ventanas deslizantes y perfiles memorizados | O(n log n) promedio |
| Paralela | Reparte grupos de usuarios independientes entre procesos | O((n log n)/p) ideal, mas el costo de los procesos |
| Final | Usa la secuencial optimizada porque fue la mas rapida al medir | O(n log n) promedio |

La version inicial es cuadratica porque Burbuja compara repetidamente elementos
vecinos y cada transaccion vuelve a buscar su historial. La version optimizada
usa Quicksort, que divide la lista alrededor de un pivote y tarda O(n log n) en
promedio. Despues, cada transaccion entra y sale una sola vez de cada ventana.

## Algoritmos comparados

- Ordenamiento Burbuja: es sencillo, pero realiza O(n^2) comparaciones. Se usa
  en la version inicial.
- Quicksort: aplica divide y conquista y tarda O(n log n) en promedio. Se usa en
  la version optimizada porque escala mejor cuando aumentan las transacciones.

Ordenar por tiempo es necesario para detectar correctamente operaciones que
ocurren dentro de ventanas de 60, 120 o 300 segundos.

## Decisiones que hay que explicar

- `dict`: agrupa transacciones por usuario y cuenta firmas y ubicaciones con
  acceso O(1) promedio.
- `deque`: representa ventanas temporales; eliminar el elemento mas antiguo es
  O(1), mientras que en una lista seria O(n).
- `set`: evita emitir dos veces la misma alerta.
- Memoizacion y cache LRU: `CachePerfiles` calcula una sola vez el promedio,
  desviacion y limite de cada usuario. Tiene capacidad limitada a 1024 perfiles
  y se invalida al cargar un conjunto nuevo, evitando datos viejos.
- Paralelismo: cada usuario se puede analizar independientemente. Se usa
  `ProcessPoolExecutor`, adecuado para trabajo de CPU y sin la limitacion del
  GIL de los hilos de Python.
- Estrategia final: los procesos agregan costo de creacion y transferencia. Las
  mediciones mostraron que ese costo supera el beneficio con estos datos, por
  eso la version final usa el algoritmo secuencial optimizado. La version
  paralela se conserva para medir y explicar ese trade-off.

## Medicion y perfilado

El benchmark mide tiempo con `time.perf_counter` y memoria Python maxima con
`tracemalloc`. Guarda la tabla obligatoria en `resultados/comparacion.csv`. En
la version paralela, `tracemalloc` mide el proceso principal y no la memoria de
los procesos hijos; esta limitacion debe aclararse al presentar los resultados.

El comando `perfilado` utiliza `cProfile` sobre la implementacion inicial y la
optimizada. Muestra las 15 funciones con mayor tiempo acumulado y guarda dos
archivos `.prof` y un resumen de texto en `resultados/`.

El comando `escalabilidad` repite la comparacion con 1.000, 2.500 y 5.000
transacciones. Guarda `resultados/escalabilidad.csv` y el grafico
`resultados/escalabilidad.png` para demostrar que la mejora se mantiene al
aumentar el volumen.

La explicacion completa de cada requisito se encuentra en
`INFORME_TECNICO.md`.

## Presentacion

El PowerPoint para la exposicion se encuentra en
`presentacion/Parcial-1-Programacion-Eficiente.pptx`. Contiene las diez
secciones solicitadas, una diapositiva adicional de escalabilidad y notas del
orador para una presentacion de aproximadamente 10 a 12 minutos.
