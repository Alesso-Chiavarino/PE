Rendimiento y memoria
=====================

Benchmark
---------

``scripts.verificar_rendimiento`` ejecuta varias repeticiones, utiliza la
mediana y compara la versión optimizada con la inicial dentro del mismo entorno.
El control falla si ambas versiones producen resultados diferentes o si la
optimizada tarda más que la inicial con una tolerancia del 25 por ciento.

Profiling
---------

``main.py perfilado`` utiliza cProfile para las versiones inicial y optimizada.
Guarda archivos ``.prof`` y un resumen ordenado por tiempo acumulado. Los archivos
pueden abrirse localmente con SnakeViz.

Memoria
-------

``scripts.verificar_memoria`` genera y analiza 20.000 transacciones mediante
streaming. ``tracemalloc`` registra el pico de memoria Python y el pipeline aplica
un límite de 25 MiB. El límite mide el heap de Python y no sustituye la medición RSS
del proceso que ofrece ``monitoreo.py`` mediante psutil.

Comandos
--------

::

   python -m scripts.verificar_rendimiento
   python -m scripts.verificar_memoria
   python main.py perfilado --transacciones 1000 --salida reportes/perfilado
