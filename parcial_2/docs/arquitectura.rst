Arquitectura
============

El sistema genera transacciones simuladas y detecta montos altos, ráfagas de
operaciones, repeticiones y cambios de ubicación casi simultáneos. Puede operar
con listas en memoria o con archivos CSV grandes procesados mediante buffers,
generadores y lotes.

Componentes
-----------

``main.py``
   Expone la interfaz de línea de comandos y coordina los casos de uso.

``generador.py``
   Produce transacciones repetibles para demostraciones, pruebas y benchmarks.

``detectores.py``
   Contiene las implementaciones inicial, optimizada y paralela. La clase
   ``EstadoDeteccionUsuario`` conserva las ventanas temporales.

``archivos.py``
   Lee y escribe CSV con buffer y procesa lotes sin cargar el archivo completo.

``medicion.py``, ``monitoreo.py`` y ``perfilado.py``
   Miden tiempo, memoria, CPU, entrada/salida y funciones costosas.

``interfaz/``
   Presenta las operaciones principales en una ventana Tkinter sin mezclar la
   interfaz con el motor de detección.

``tests/``
   Verifica correctitud, equivalencia entre versiones, archivos y monitoreo.

``scripts/``
   Implementa los controles reproducibles de complejidad, rendimiento y memoria.

Flujo principal
---------------

::

   CLI o interfaz
        |
        v
   generador o lector CSV ---> detector ---> alertas CSV o pantalla
        |                         |
        +---- medición -----------+
                  |
                  v
               reportes

La integración continua ejecuta primero calidad estática, pruebas y seguridad.
El benchmark, el profiling y la memoria se ejecutan después porque son controles
más costosos.
