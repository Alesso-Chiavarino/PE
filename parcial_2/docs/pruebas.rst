Pruebas y cobertura
===================

Estrategia
----------

El proyecto utiliza pytest como framework. Las pruebas comparan todas las
implementaciones, verifican los cuatro patrones sospechosos, ejercitan la caché,
validan el procesamiento por lotes y comprueban las métricas de recursos.

Ejecución local
---------------

::

   python -m pytest --cov --cov-fail-under=90 --cov-report=term-missing

El pipeline rechaza un cambio si falla una prueba o si la cobertura de los módulos
principales queda por debajo del 90 por ciento. También genera ``pytest.xml`` y
``coverage.xml`` como reportes descargables.

Resultados de referencia
------------------------

La línea base del inicio del tercer parcial contiene 15 pruebas aprobadas y una
cobertura total del 94 por ciento en los módulos principales. Estos valores pueden
aumentar, pero el umbral de aprobación permanece en 90 por ciento.
