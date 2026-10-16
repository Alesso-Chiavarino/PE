"""Pruebas de regresion para los detectores en memoria."""

import pytest

from algoritmos_ordenamiento import ordenar_burbuja, ordenar_quicksort
from detectores import (
    CachePerfiles,
    detectar_con_estructuras,
    detectar_inicial,
    detectar_optimizado,
    detectar_paralelo,
)
from generador import generar_transacciones
from medicion import ejecutar_escalabilidad
from modelos import Transaccion


@pytest.fixture(scope="module")
def transacciones() -> list[Transaccion]:
    """Crea un conjunto compartido y reproducible para las pruebas."""
    return generar_transacciones(500, semilla=7)


def test_todas_las_versiones_encuentran_lo_mismo(
    transacciones: list[Transaccion],
) -> None:
    inicial = detectar_inicial(transacciones)
    estructuras = detectar_con_estructuras(transacciones)
    optimizada = detectar_optimizado(transacciones)
    paralela = detectar_paralelo(transacciones, trabajadores=2)

    assert inicial == estructuras == optimizada == paralela


def test_detecta_los_cuatro_patrones(transacciones: list[Transaccion]) -> None:
    tipos = {alerta.tipo for alerta in detectar_optimizado(transacciones)}
    assert tipos == {
        "MONTO_ALTO",
        "RAFAGA",
        "OPERACION_REPETIDA",
        "UBICACIONES_SIMULTANEAS",
    }


def test_la_cache_reutiliza_perfiles(transacciones: list[Transaccion]) -> None:
    cache = CachePerfiles()
    detectar_optimizado(transacciones, cache)
    aciertos, fallos = cache.estadisticas()

    assert aciertos > 0
    assert fallos > 0
    assert aciertos + fallos == len(transacciones)


def test_la_cache_se_invalida_con_datos_nuevos() -> None:
    cache = CachePerfiles()
    primer_grupo = {
        "USR-1": [Transaccion(1, "USR-1", 1, 100.0, "A", "Cordoba")]
    }
    segundo_grupo = {
        "USR-1": [
            Transaccion(1, "USR-1", 1, 100.0, "A", "Cordoba"),
            Transaccion(2, "USR-1", 2, 5000.0, "B", "Cordoba"),
        ]
    }

    cache.cargar(primer_grupo)
    perfil_anterior = cache.obtener("USR-1")
    cache.cargar(segundo_grupo)
    perfil_nuevo = cache.obtener("USR-1")

    assert perfil_anterior.promedio != perfil_nuevo.promedio
    assert cache.estadisticas() == (0, 1)


def test_burbuja_y_quicksort_ordenan_por_tiempo(
    transacciones: list[Transaccion],
) -> None:
    tiempos_burbuja = [
        transaccion.instante for transaccion in ordenar_burbuja(transacciones)
    ]
    tiempos_quicksort = [
        transaccion.instante for transaccion in ordenar_quicksort(transacciones)
    ]

    assert tiempos_burbuja == sorted(tiempos_burbuja)
    assert tiempos_burbuja == tiempos_quicksort


def test_escalabilidad_compara_los_mismos_resultados() -> None:
    resultados = ejecutar_escalabilidad([100, 200], semilla=7)

    assert [resultado.transacciones for resultado in resultados] == [100, 200]
    assert all(resultado.tiempo_inicial > 0 for resultado in resultados)
    assert all(resultado.tiempo_optimizado > 0 for resultado in resultados)
