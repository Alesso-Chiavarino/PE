import cProfile
import io
import pstats
from collections.abc import Callable
from pathlib import Path

from detectores import CachePerfiles, detectar_inicial, detectar_optimizado
from generador import generar_transacciones
from modelos import Alerta, Transaccion


# ==============================================================================
# 8. PERFILADO DE CODIGO CON cProfile Y pstats (DETECCION DE BOTTLENECKS)
# ==============================================================================
def _perfilar(
    nombre: str,
    funcion: Callable[[list[Transaccion]], list[Alerta]],
    transacciones: list[Transaccion],
    carpeta: Path,
) -> tuple[list[Alerta], str, Path]:
    """
    [CRITERIO: PERFILADO DEL CODIGO]
    - cProfile: Perfilador deterministico de Python a nivel de llamada de funcion.
      Mide cantidad de llamadas (ncalls), tiempo propio (tottime) y tiempo acumulado (cumtime).
    - pstats: Formatea y ordena las estadisticas por tiempo acumulado ('cumulative').
    - Objetivo: Identificar cientificamente el cuello de botella (bottleneck).
      En la version inicial, cProfile expone que ordenar_burbuja y los list-comprehensions
      consumen mas del 90% del tiempo de CPU.
    """
    perfilador = cProfile.Profile()
    alertas = perfilador.runcall(funcion, transacciones)

    # Persistencia de estadisticas binarias para herramientas como SnakeViz
    ruta = carpeta / f"perfilado_{nombre}.prof"
    perfilador.dump_stats(ruta)

    # Exportacion de las 15 funciones mas pesadas a texto
    texto = io.StringIO()
    pstats.Stats(perfilador, stream=texto).sort_stats("cumulative").print_stats(15)
    return alertas, texto.getvalue(), ruta


def ejecutar_perfilado_comparativo(
    cantidad: int, semilla: int, carpeta: Path
) -> None:
    carpeta.mkdir(parents=True, exist_ok=True)
    transacciones = generar_transacciones(cantidad, semilla)

    alertas_iniciales, resumen_inicial, ruta_inicial = _perfilar(
        "inicial", detectar_inicial, transacciones, carpeta
    )

    cache = CachePerfiles()

    def optimizada(datos: list[Transaccion]) -> list[Alerta]:
        return detectar_optimizado(datos, cache)

    alertas_optimizadas, resumen_optimizado, ruta_optimizada = _perfilar(
        "optimizado", optimizada, transacciones, carpeta
    )

    if alertas_iniciales != alertas_optimizadas:
        raise RuntimeError("Las versiones produjeron alertas diferentes")

    aciertos, fallos = cache.estadisticas()
    resumen = (
        "PERFILADO DE LA IMPLEMENTACION INICIAL\n"
        f"{resumen_inicial}\n"
        "PERFILADO DEL ALGORITMO OPTIMIZADO\n"
        f"{resumen_optimizado}\n"
        f"Cache de perfiles: {aciertos} aciertos y {fallos} fallos\n"
    )
    ruta_resumen = carpeta / "perfilado_resumen.txt"
    ruta_resumen.write_text(resumen, encoding="utf-8")

    print(f"Transacciones: {cantidad}")
    print(f"Alertas iguales en ambas versiones: {len(alertas_iniciales)}")
    print(f"Cache de perfiles: {aciertos} aciertos, {fallos} fallos")
    print(resumen)
    print(f"Perfil inicial guardado en: {ruta_inicial}")
    print(f"Perfil optimizado guardado en: {ruta_optimizada}")
    print(f"Resumen guardado en: {ruta_resumen}")
