"""Mide el pico de memoria del procesamiento CSV por streaming."""

from __future__ import annotations

import argparse
import json
import tempfile
import tracemalloc
from pathlib import Path

from archivos import guardar_transacciones_csv, iterar_alertas_csv
from generador import iterar_transacciones_ordenadas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transacciones", type=int, default=20_000)
    parser.add_argument("--lote", type=int, default=10_000)
    parser.add_argument("--limite-mb", type=float, default=25.0)
    parser.add_argument("--salida", type=Path, default=Path("reportes/memoria.json"))
    argumentos = parser.parse_args()

    with tempfile.TemporaryDirectory() as temporal:
        ruta_csv = Path(temporal) / "transacciones.csv"
        guardar_transacciones_csv(
            iterar_transacciones_ordenadas(argumentos.transacciones), ruta_csv
        )
        tracemalloc.start()
        cantidad_alertas = sum(1 for _ in iterar_alertas_csv(ruta_csv, argumentos.lote))
        _, memoria_pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    memoria_mb = memoria_pico / (1024 * 1024)
    reporte = {
        "transacciones": argumentos.transacciones,
        "lote": argumentos.lote,
        "alertas": cantidad_alertas,
        "memoria_pico_mb": memoria_mb,
        "limite_mb": argumentos.limite_mb,
    }
    argumentos.salida.parent.mkdir(parents=True, exist_ok=True)
    argumentos.salida.write_text(json.dumps(reporte, indent=2), encoding="utf-8")

    print(f"Memoria Python máxima: {memoria_mb:.2f} MB (límite {argumentos.limite_mb:.2f} MB)")
    if memoria_mb > argumentos.limite_mb:
        raise SystemExit("El procesamiento superó el límite de memoria")


if __name__ == "__main__":
    main()
