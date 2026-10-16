"""Monitoreo liviano de recursos con psutil."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

import psutil


@dataclass(frozen=True, slots=True)
class MetricasRecursos:
    """Resume los recursos consumidos por una operacion."""

    tiempo_segundos: float
    memoria_rss_maxima_mb: float
    cpu_segundos: float
    bytes_leidos: int
    bytes_escritos: int


def _obtener_contadores_io(proceso: psutil.Process) -> tuple[int, int]:
    """Obtiene E/S por proceso cuando el sistema operativo la ofrece."""
    obtener = getattr(proceso, "io_counters", None)
    if obtener is None:
        return 0, 0
    contadores = obtener()
    return contadores.read_bytes, contadores.write_bytes


def medir_recursos(
    operacion: Callable[[], int], intervalo: float = 0.01
) -> tuple[int, MetricasRecursos]:
    """Ejecuta una operacion y observa memoria, CPU y E/S del proceso."""
    proceso = psutil.Process()
    detener = threading.Event()
    memoria_maxima = proceso.memory_info().rss

    def observar_memoria() -> None:
        nonlocal memoria_maxima
        while not detener.wait(intervalo):
            memoria_maxima = max(memoria_maxima, proceso.memory_info().rss)

    cpu_inicial = proceso.cpu_times()
    leidos_iniciales, escritos_iniciales = _obtener_contadores_io(proceso)
    inicio = time.perf_counter()
    observador = threading.Thread(target=observar_memoria, daemon=True)
    observador.start()
    try:
        resultado = operacion()
    finally:
        detener.set()
        observador.join()

    duracion = time.perf_counter() - inicio
    memoria_maxima = max(memoria_maxima, proceso.memory_info().rss)
    cpu_final = proceso.cpu_times()
    leidos_finales, escritos_finales = _obtener_contadores_io(proceso)
    metricas = MetricasRecursos(
        tiempo_segundos=duracion,
        memoria_rss_maxima_mb=memoria_maxima / (1024 * 1024),
        cpu_segundos=(cpu_final.user + cpu_final.system)
        - (cpu_inicial.user + cpu_inicial.system),
        bytes_leidos=leidos_finales - leidos_iniciales,
        bytes_escritos=escritos_finales - escritos_iniciales,
    )
    return resultado, metricas
