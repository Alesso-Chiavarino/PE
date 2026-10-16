import argparse
from collections import Counter
from pathlib import Path

from archivos import guardar_alertas_csv, guardar_transacciones_csv, iterar_alertas_csv
from detectores import detectar_final
from generador import generar_transacciones, iterar_transacciones_ordenadas
from medicion import (
    ejecutar_comparacion,
    ejecutar_escalabilidad,
    guardar_csv,
    guardar_escalabilidad_csv,
    guardar_grafico,
    guardar_grafico_escalabilidad,
    mostrar_escalabilidad,
    mostrar_tabla,
)
from monitoreo import medir_recursos
from perfilado import ejecutar_perfilado_comparativo


def ejecutar_demo(cantidad: int, semilla: int, trabajadores: int | None) -> None:
    transacciones = generar_transacciones(cantidad, semilla)
    alertas, estrategia = detectar_final(transacciones, trabajadores)
    cantidades = Counter(alerta.tipo for alerta in alertas)

    print(f"Transacciones procesadas: {len(transacciones)}")
    print(f"Estrategia elegida: {estrategia}")
    print(f"Alertas encontradas: {len(alertas)}")
    for tipo, total in sorted(cantidades.items()):
        print(f"  {tipo:<25} {total}")

    print("\nPrimeras alertas:")
    for alerta in alertas[:10]:
        print(
            f"  TX {alerta.transaccion_id:>5} | {alerta.usuario:<12} | "
            f"{alerta.tipo:<25} | {alerta.detalle}"
        )


def ejecutar_benchmark(
    cantidad: int, semilla: int, trabajadores: int | None, salida: Path
) -> None:
    resultados = ejecutar_comparacion(cantidad, trabajadores, semilla)
    mostrar_tabla(resultados)

    ruta_csv = salida / "comparacion.csv"
    ruta_grafico = salida / "comparacion_tiempos.png"
    guardar_csv(resultados, ruta_csv)
    print(f"\nTabla guardada en: {ruta_csv}")

    if guardar_grafico(resultados, ruta_grafico):
        print(f"Grafico guardado en: {ruta_grafico}")
    else:
        print("Grafico omitido: instalar dependencias con pip install -r requirements.txt")


def ejecutar_perfilado(cantidad: int, semilla: int, salida: Path) -> None:
    ejecutar_perfilado_comparativo(cantidad, semilla, salida)


def ejecutar_prueba_escalabilidad(
    cantidades: list[int], semilla: int, salida: Path
) -> None:
    resultados = ejecutar_escalabilidad(cantidades, semilla)
    mostrar_escalabilidad(resultados)

    ruta_csv = salida / "escalabilidad.csv"
    ruta_grafico = salida / "escalabilidad.png"
    guardar_escalabilidad_csv(resultados, ruta_csv)
    print(f"\nTabla guardada en: {ruta_csv}")

    if guardar_grafico_escalabilidad(resultados, ruta_grafico):
        print(f"Grafico guardado en: {ruta_grafico}")
    else:
        print("Grafico omitido: instalar dependencias con pip install -r requirements.txt")


def ejecutar_generacion_archivo(cantidad: int, semilla: int, salida: Path) -> None:
    """Genera un CSV cronologico usando un iterador de memoria acotada."""
    total = guardar_transacciones_csv(
        iterar_transacciones_ordenadas(cantidad, semilla), salida
    )
    print(f"Transacciones generadas: {total}")
    print(f"Archivo guardado en: {salida}")


def ejecutar_analisis_archivo(entrada: Path, salida: Path, lote: int) -> None:
    """Procesa un CSV por lotes y escribe las alertas progresivamente."""
    def procesar() -> int:
        return guardar_alertas_csv(iterar_alertas_csv(entrada, lote), salida)

    total_alertas, metricas = medir_recursos(procesar)
    print(f"Alertas encontradas: {total_alertas}")
    print(f"Tamaño de lote: {lote}")
    print(f"Tiempo total: {metricas.tiempo_segundos:.4f} s")
    print(f"Memoria RSS maxima: {metricas.memoria_rss_maxima_mb:.2f} MB")
    print(f"Tiempo de CPU: {metricas.cpu_segundos:.4f} s")
    print(f"Bytes leidos: {metricas.bytes_leidos}")
    print(f"Bytes escritos: {metricas.bytes_escritos}")
    print(f"Archivo guardado en: {salida}")


def _agregar_datos_generados(parser: argparse.ArgumentParser) -> None:
    """Agrega argumentos compartidos por los comandos que generan datos."""
    parser.add_argument("--transacciones", type=int, default=5000)
    parser.add_argument("--semilla", type=int, default=42)


def crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detector eficiente de transacciones sospechosas"
    )
    subcomandos = parser.add_subparsers(dest="comando", required=True)

    demo = subcomandos.add_parser("demo", help="Ejecutar una demostracion")
    _agregar_datos_generados(demo)
    demo.add_argument("--trabajadores", type=int)

    benchmark = subcomandos.add_parser("benchmark", help="Comparar las cinco versiones")
    _agregar_datos_generados(benchmark)
    benchmark.add_argument("--trabajadores", type=int)
    benchmark.add_argument("--salida", type=Path, default=Path("resultados"))

    perfilado = subcomandos.add_parser(
        "perfilado", help="Perfilar las versiones inicial y optimizada"
    )
    _agregar_datos_generados(perfilado)
    perfilado.add_argument("--salida", type=Path, default=Path("resultados"))

    escalabilidad = subcomandos.add_parser(
        "escalabilidad", help="Medir el crecimiento al aumentar los datos"
    )
    escalabilidad.add_argument(
        "--volumenes", type=int, nargs="+", default=[1000, 2500, 5000]
    )
    escalabilidad.add_argument("--semilla", type=int, default=42)
    escalabilidad.add_argument("--salida", type=Path, default=Path("resultados"))

    generar_archivo = subcomandos.add_parser(
        "generar-archivo", help="Generar un CSV grande sin conservarlo en memoria"
    )
    _agregar_datos_generados(generar_archivo)
    generar_archivo.add_argument(
        "--salida", type=Path, default=Path("datos/transacciones.csv")
    )

    analizar_archivo = subcomandos.add_parser(
        "analizar-archivo", help="Procesar un CSV cronologico por lotes"
    )
    analizar_archivo.add_argument("entrada", type=Path)
    analizar_archivo.add_argument(
        "--salida", type=Path, default=Path("resultados/alertas.csv")
    )
    analizar_archivo.add_argument("--lote", type=int, default=10_000)

    subcomandos.add_parser("interfaz", help="Abrir la interfaz grafica nativa")

    return parser


def main() -> None:
    argumentos = crear_parser().parse_args()

    if argumentos.comando == "demo":
        ejecutar_demo(
            argumentos.transacciones, argumentos.semilla, argumentos.trabajadores
        )
    elif argumentos.comando == "benchmark":
        ejecutar_benchmark(
            argumentos.transacciones,
            argumentos.semilla,
            argumentos.trabajadores,
            argumentos.salida,
        )
    elif argumentos.comando == "perfilado":
        ejecutar_perfilado(
            argumentos.transacciones, argumentos.semilla, argumentos.salida
        )
    elif argumentos.comando == "escalabilidad":
        ejecutar_prueba_escalabilidad(
            argumentos.volumenes, argumentos.semilla, argumentos.salida
        )
    elif argumentos.comando == "generar-archivo":
        ejecutar_generacion_archivo(
            argumentos.transacciones, argumentos.semilla, argumentos.salida
        )
    elif argumentos.comando == "analizar-archivo":
        ejecutar_analisis_archivo(
            argumentos.entrada, argumentos.salida, argumentos.lote
        )
    else:
        from interfaz.ventana import iniciar_interfaz

        iniciar_interfaz()


if __name__ == "__main__":
    main()
