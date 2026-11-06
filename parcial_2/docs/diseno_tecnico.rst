Diseño técnico
==============

Estructuras de datos
--------------------

``dict`` agrupa transacciones por usuario y permite búsquedas de costo promedio
constante. ``deque`` representa ventanas temporales y elimina elementos antiguos
en tiempo constante. ``set`` evita alertas duplicadas. ``CachePerfiles`` limita
la memoria utilizada por los perfiles calculados.

Algoritmos
----------

La versión inicial utiliza ordenamiento Burbuja y sirve como línea base de
complejidad cuadrática. La versión optimizada utiliza Quicksort y ventanas
deslizantes, con complejidad promedio ``O(n log n)``. La implementación paralela
reparte usuarios entre procesos, aunque para volúmenes pequeños el costo de crear
procesos puede superar el beneficio.

Archivos grandes
----------------

El lector usa un buffer de un MiB para reducir operaciones pequeñas de entrada y
salida. Los generadores entregan una transacción por vez y ``agrupar_en_lotes``
forma lotes configurables. El estado temporal se conserva entre lotes, por lo que
una alerta puede considerar transacciones ubicadas a ambos lados de un límite.

Contratos principales
---------------------

Los detectores reciben una lista de ``Transaccion`` y devuelven una lista de
``Alerta``. El procesamiento CSV requiere un archivo cronológicamente ordenado y
genera ``ValueError`` si el orden o el tamaño del lote son inválidos. La referencia
completa de funciones, parámetros y retornos se encuentra en :doc:`api`.
