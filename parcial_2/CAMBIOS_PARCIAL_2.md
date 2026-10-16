# Cambios realizados para el segundo parcial

## Resumen

La version del primer parcial cargaba todas las transacciones en memoria y la
logica de las ventanas temporales solo podia ejecutarse sobre una lista completa.
La segunda version separa el estado de deteccion, agrega procesamiento de CSV
grandes y utiliza pytest como framework de pruebas.

## Refactorizaciones que se pueden explicar

| Antes | Despues | Motivo |
|---|---|---|
| Umbrales definidos como constantes dispersas | `ConfiguracionDeteccion` centraliza los valores | Facilita cambios y pruebas |
| `_detectar_grupo` administraba todas las colas y contadores | `EstadoDeteccionUsuario` encapsula el estado | Permite reutilizar la deteccion en memoria y streaming |
| Argumentos `--transacciones` y `--semilla` repetidos en el parser | `_agregar_datos_generados` los define una vez | Aplica DRY |
| Dos funciones repetian la escritura de CSV | `_guardar_filas_csv` concentra la operacion | Reduce codigo duplicado |
| Dos graficos repetian la configuracion de Matplotlib | `_cargar_pyplot` configura el backend y cache | Evita configuracion redundante |
| Pruebas agrupadas en una clase `unittest` | Funciones, fixtures y parametrizacion de pytest | Casos mas breves y faciles de ampliar |
| Generacion completa en una lista | `iterar_transacciones_ordenadas` entrega un elemento por vez | Reduce memoria al generar archivos |

## Funcionalidades nuevas

- `generar-archivo` recibe la cantidad mediante `--transacciones`.
- `analizar-archivo` procesa un CSV con un tamaño configurable mediante `--lote`.
- La lectura y escritura usan un buffer de 1 MB.
- Los perfiles se calculan incrementalmente en una primera pasada.
- La segunda pasada conserva las ventanas entre lotes, por lo que no pierde
  alertas en sus limites.
- Sphinx genera la documentacion HTML desde los docstrings.

## Herramientas elegidas

- pytest y pytest-cov para testing y cobertura.
- SnakeViz para visualizar los perfiles de `cProfile` ya generados.
- psutil para medir memoria RSS, CPU y operaciones de E/S.
- flake8 para PEP 8 y analisis estatico.
- Sphinx para documentacion automatica.

Estas herramientas aparecen en el material de clase y requieren poca
configuracion adicional.
