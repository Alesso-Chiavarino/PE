from __future__ import annotations

import csv
import os
import time
import tracemalloc
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from detectores import (
    detectar_con_estructuras,
    detectar_final,
    detectar_inicial,
    detectar_optimizado,
    detectar_paralelo,
)
from generador import generar_transacciones
from modelos import Alerta, Transaccion


@dataclass(frozen=True, slots=True)
class ResultadoMedicion:
    version: str
    tiempo_segundos: float
    memoria_mb: float
    cantidad_alertas: int
    observacion: str


@dataclass(frozen=True, slots=True)
class ResultadoEscalabilidad:
    transacciones: int
    tiempo_inicial: float
    tiempo_optimizado: float
    mejora: float


def _medir(
    version: str,
    funcion: Callable[[list[Transaccion]], list[Alerta]],
    transacciones: list[Transaccion],
    observacion: str,
) -> tuple[ResultadoMedicion, list[Alerta]]:
    tracemalloc.start()
    inicio = time.perf_counter()
    alertas = funcion(transacciones)
    tiempo = time.perf_counter() - inicio
    _, memoria_maxima = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    resultado = ResultadoMedicion(
        version,
        tiempo,
        memoria_maxima / (1024 * 1024),
        len(alertas),
        observacion,
    )
    return resultado, alertas


def ejecutar_comparacion(
    cantidad: int, trabajadores: int | None = None, semilla: int = 42
) -> list[ResultadoMedicion]:
    transacciones = generar_transacciones(cantidad, semilla)
    cpu = trabajadores or min(4, os.cpu_count() or 1)

    versiones: list[
        tuple[str, Callable[[list[Transaccion]], list[Alerta]], str]
    ] = [
        (
            "Implementacion inicial",
            detectar_inicial,
            "Baseline: Burbuja y busquedas repetidas",
        ),
        (
            "Estructura optimizada",
            detectar_con_estructuras,
            "Mejora de busqueda con dict, deque y set",
        ),
        (
            "Algoritmo optimizado",
            detectar_optimizado,
            "Quicksort y cache: mejor escalabilidad",
        ),
        (
            "Concurrencia/paralelismo",
            lambda datos: detectar_paralelo(datos, trabajadores),
            f"{cpu} procesos; se evalua el overhead",
        ),
        (
            "Version final",
            lambda datos: detectar_final(datos, trabajadores)[0],
            "Optimizada secuencial: menor tiempo medido",
        ),
    ]

    resultados: list[ResultadoMedicion] = []
    alertas_referencia: list[Alerta] | None = None

    for nombre, funcion, observacion in versiones:
        resultado, alertas = _medir(nombre, funcion, transacciones, observacion)
        if alertas_referencia is None:
            alertas_referencia = alertas
        elif alertas != alertas_referencia:
            raise RuntimeError(f"La version {nombre} produjo alertas diferentes")
        resultados.append(resultado)

    return resultados


def ejecutar_escalabilidad(
    cantidades: list[int], semilla: int = 42
) -> list[ResultadoEscalabilidad]:
    resultados: list[ResultadoEscalabilidad] = []

    for cantidad in cantidades:
        transacciones = generar_transacciones(cantidad, semilla)

        inicio = time.perf_counter()
        alertas_iniciales = detectar_inicial(transacciones)
        tiempo_inicial = time.perf_counter() - inicio

        inicio = time.perf_counter()
        alertas_optimizadas = detectar_optimizado(transacciones)
        tiempo_optimizado = time.perf_counter() - inicio

        if alertas_iniciales != alertas_optimizadas:
            raise RuntimeError("Las versiones produjeron alertas diferentes")

        resultados.append(
            ResultadoEscalabilidad(
                cantidad,
                tiempo_inicial,
                tiempo_optimizado,
                tiempo_inicial / tiempo_optimizado,
            )
        )

    return resultados


def guardar_csv(resultados: list[ResultadoMedicion], ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(
            ["Version", "Tiempo (s)", "Memoria (MB)", "Alertas", "Observacion"]
        )
        for resultado in resultados:
            escritor.writerow(
                [
                    resultado.version,
                    f"{resultado.tiempo_segundos:.6f}",
                    f"{resultado.memoria_mb:.3f}",
                    resultado.cantidad_alertas,
                    resultado.observacion,
                ]
            )


def guardar_escalabilidad_csv(
    resultados: list[ResultadoEscalabilidad], ruta: Path
) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(
            ["Transacciones", "Inicial (s)", "Optimizada (s)", "Mejora (veces)"]
        )
        for resultado in resultados:
            escritor.writerow(
                [
                    resultado.transacciones,
                    f"{resultado.tiempo_inicial:.6f}",
                    f"{resultado.tiempo_optimizado:.6f}",
                    f"{resultado.mejora:.2f}",
                ]
            )


def mostrar_tabla(resultados: list[ResultadoMedicion]) -> None:
    encabezado = (
        f"{'VERSION':<25} {'TIEMPO':>10} {'MEMORIA':>11} "
        f"{'ALERTAS':>9}  OBSERVACION"
    )
    print(encabezado)
    print("-" * len(encabezado))
    for resultado in resultados:
        print(
            f"{resultado.version:<25} "
            f"{resultado.tiempo_segundos:>9.4f}s "
            f"{resultado.memoria_mb:>9.2f}MB "
            f"{resultado.cantidad_alertas:>9}  "
            f"{resultado.observacion}"
        )


def mostrar_escalabilidad(resultados: list[ResultadoEscalabilidad]) -> None:
    print(f"{'TRANSACCIONES':>14} {'INICIAL':>12} {'OPTIMIZADA':>12} {'MEJORA':>10}")
    print("-" * 54)
    for resultado in resultados:
        print(
            f"{resultado.transacciones:>14} "
            f"{resultado.tiempo_inicial:>11.4f}s "
            f"{resultado.tiempo_optimizado:>11.4f}s "
            f"{resultado.mejora:>8.1f}x"
        )


def guardar_grafico(resultados: list[ResultadoMedicion], ruta: Path) -> bool:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    cache_grafico = ruta.parent / ".cache_grafico"
    cache_grafico.mkdir(exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cache_grafico))
    os.environ.setdefault("XDG_CACHE_HOME", str(cache_grafico))
    os.environ.setdefault("MPLBACKEND", "Agg")

    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        return False

    nombres = [resultado.version for resultado in resultados]
    tiempos = [resultado.tiempo_segundos for resultado in resultados]

    figura, eje = plt.subplots(figsize=(9, 5))
    barras = eje.bar(nombres, tiempos, color=["#d95f02", "#7570b3", "#1b9e77", "#e6ab02", "#2a6f97"])
    eje.set_title("Tiempo por version")
    eje.set_ylabel("Segundos")
    eje.tick_params(axis="x", rotation=15)
    eje.bar_label(barras, fmt="%.4f s", padding=3)
    figura.tight_layout()
    figura.savefig(ruta, dpi=160)
    plt.close(figura)
    return True


def guardar_grafico_escalabilidad(
    resultados: list[ResultadoEscalabilidad], ruta: Path
) -> bool:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    cache_grafico = ruta.parent / ".cache_grafico"
    cache_grafico.mkdir(exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cache_grafico))
    os.environ.setdefault("XDG_CACHE_HOME", str(cache_grafico))
    os.environ.setdefault("MPLBACKEND", "Agg")

    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        return False

    cantidades = [resultado.transacciones for resultado in resultados]
    iniciales = [resultado.tiempo_inicial for resultado in resultados]
    optimizados = [resultado.tiempo_optimizado for resultado in resultados]

    figura, eje = plt.subplots(figsize=(8, 5))
    eje.plot(cantidades, iniciales, marker="o", label="Implementacion inicial")
    eje.plot(cantidades, optimizados, marker="o", label="Version optimizada")
    eje.set_title("Escalabilidad por cantidad de transacciones")
    eje.set_xlabel("Transacciones")
    eje.set_ylabel("Segundos")
    eje.legend()
    eje.grid(alpha=0.25)
    figura.tight_layout()
    figura.savefig(ruta, dpi=160)
    plt.close(figura)
    return True
