Refactorizacion del segundo parcial
===================================

La clase ``EstadoDeteccionUsuario`` concentra las ventanas temporales, los
contadores y la deduplicacion de alertas. La deteccion en memoria y la deteccion
desde CSV reutilizan esta clase. Antes, toda esa logica estaba acoplada a una
lista completa de transacciones.

La configuracion de los umbrales se traslado a ``ConfiguracionDeteccion``. Esto
elimina constantes dispersas y permite probar configuraciones alternativas.

La escritura de resultados y la preparacion de Matplotlib se centralizaron en
funciones comunes. De esta manera, las tablas y graficos no repiten la apertura
de archivos ni la configuracion del backend.
