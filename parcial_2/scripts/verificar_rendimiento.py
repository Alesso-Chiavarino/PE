"""Compara el detector inicial con el optimizado y guarda una línea base relativa."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from collections.abc import Callable
from pathlib import Path

from detectores import detectar_inicial, detectar_optimizado
from generador import generar_transacciones
from modelos import Alerta, Transaccion


def medir(
    funcion: Callable[[list[Transaccion]], list[Alerta]],
    datos: list[Transaccion],
    repeticiones: int,
) -> tuple[float, list[Alerta]]:
    """Devuelve la mediana para reducir el ruido del entorno de CI."""
    tiempos: list[float] = []
    resultado: list[Alerta] = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        resultado = funcion(datos)
        tiempos.append(time.perf_counter() - inicio)
    return statistics.median(tiempos), resultado


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transacciones", type=int, default=2_500)
    parser.add_argument("--repeticiones", type=int, default=3)
    parser.add_argument("--tolerancia", type=float, default=1.25)
    parser.add_argument("--salida", type=Path, default=Path("reportes/rendimiento.json"))
    argumentos = parser.parse_args()

    datos = generar_transacciones(argumentos.transacciones, semilla=42)
    tiempo_inicial, alertas_iniciales = medir(detectar_inicial, datos, argumentos.repeticiones)
    tiempo_optimizado, alertas_optimizadas = medir(
        detectar_optimizado, datos, argumentos.repeticiones
    )
    reporte = {
        "transacciones": argumentos.transacciones,
        "repeticiones": argumentos.repeticiones,
        "tiempo_inicial_mediana": tiempo_inicial,
        "tiempo_optimizado_mediana": tiempo_optimizado,
        "mejora": tiempo_inicial / tiempo_optimizado,
        "tolerancia": argumentos.tolerancia,
    }
    argumentos.salida.parent.mkdir(parents=True, exist_ok=True)
    argumentos.salida.write_text(json.dumps(reporte, indent=2), encoding="utf-8")

    print(f"Versión inicial: {tiempo_inicial:.6f} s")
    print(f"Versión optimizada: {tiempo_optimizado:.6f} s")
    print(f"Mejora: {reporte['mejora']:.2f}x")
    if alertas_iniciales != alertas_optimizadas:
        raise SystemExit("Las versiones produjeron resultados diferentes")
    if tiempo_optimizado > tiempo_inicial * argumentos.tolerancia:
        raise SystemExit("Se detectó una regresión significativa de rendimiento")


if __name__ == "__main__":
    main()
