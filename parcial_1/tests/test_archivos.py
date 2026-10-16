"""Pruebas del procesamiento bufferizado y por lotes."""

from pathlib import Path

import pytest

from archivos import (
    agrupar_en_lotes,
    guardar_transacciones_csv,
    iterar_alertas_csv,
    leer_transacciones_csv,
)
from detectores import detectar_optimizado
from generador import iterar_transacciones_ordenadas
from main import crear_parser
from modelos import Transaccion


def crear_csv_temporal(ruta: Path, cantidad: int = 500) -> list[Transaccion]:
    transacciones = list(iterar_transacciones_ordenadas(cantidad, semilla=7))
    guardar_transacciones_csv(transacciones, ruta)
    return transacciones


def test_csv_conserva_las_transacciones(tmp_path: Path) -> None:
    ruta = tmp_path / "transacciones.csv"
    originales = crear_csv_temporal(ruta, 100)

    assert list(leer_transacciones_csv(ruta)) == originales


@pytest.mark.parametrize("tamanio_lote", [1, 7, 100, 1_000])
def test_el_resultado_no_depende_del_tamanio_del_lote(
    tmp_path: Path, tamanio_lote: int
) -> None:
    ruta = tmp_path / "transacciones.csv"
    transacciones = crear_csv_temporal(ruta)
    esperadas = detectar_optimizado(transacciones)

    assert list(iterar_alertas_csv(ruta, tamanio_lote)) == esperadas


def test_lotes_rechaza_tamanio_invalido() -> None:
    with pytest.raises(ValueError, match="mayor que cero"):
        list(agrupar_en_lotes([], 0))


def test_archivo_debe_estar_ordenado(tmp_path: Path) -> None:
    ruta = tmp_path / "desordenado.csv"
    transacciones = [
        Transaccion(1, "USR-1", 20, 10.0, "A", "Cordoba"),
        Transaccion(2, "USR-1", 10, 20.0, "B", "Cordoba"),
    ]
    guardar_transacciones_csv(transacciones, ruta)

    with pytest.raises(ValueError, match="ordenado"):
        list(iterar_alertas_csv(ruta, 10))


def test_cantidad_se_puede_indicar_por_comando() -> None:
    argumentos = crear_parser().parse_args(
        ["generar-archivo", "--transacciones", "1234"]
    )

    assert argumentos.transacciones == 1234
