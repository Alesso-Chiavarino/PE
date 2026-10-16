Uso desde la consola
====================

La cantidad de transacciones se indica con ``--transacciones``.

Demostracion en memoria::

   python main.py demo --transacciones 5000

Generacion de un archivo grande::

   python main.py generar-archivo --transacciones 100000 --salida datos/transacciones.csv

Procesamiento por lotes::

   python main.py analizar-archivo datos/transacciones.csv --lote 10000

El archivo de entrada debe estar ordenado por la columna ``instante``. El
programa valida esta condicion para que las ventanas temporales produzcan
resultados correctos aunque una ventana cruce el limite entre dos lotes.

Al finalizar, el comando informa las metricas obtenidas con ``psutil``: tiempo
total, memoria RSS maxima, tiempo de CPU y bytes de entrada y salida. Algunos
sistemas, incluido macOS, no ofrecen E/S por proceso mediante ``psutil``. En
ese caso los contadores de bytes se informan como cero.
