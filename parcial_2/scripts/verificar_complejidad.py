"""Verifica la complejidad ciclomática y genera un reporte JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from radon.complexity import cc_rank, cc_visit

ARCHIVOS_EXCLUIDOS = {"scripts/verificar_complejidad.py"}


def analizar_proyecto(raiz: Path) -> dict[str, object]:
    """Analiza funciones y métodos del proyecto sin incluir pruebas ni artefactos."""
    bloques: list[dict[str, object]] = []
    complejidades: list[int] = []
    for ruta in sorted(raiz.rglob("*.py")):
        relativa = ruta.relative_to(raiz).as_posix()
        if (
            relativa in ARCHIVOS_EXCLUIDOS
            or any(parte.startswith(".") for parte in ruta.relative_to(raiz).parts)
            or ruta.parts[-2:-1] == ("tests",)
            or "docs" in ruta.parts
            or "resultados" in ruta.parts
        ):
            continue
        for bloque in cc_visit(ruta.read_text(encoding="utf-8")):
            complejidades.append(bloque.complexity)
            bloques.append(
                {
                    "archivo": relativa,
                    "nombre": bloque.name,
                    "linea": bloque.lineno,
                    "complejidad": bloque.complexity,
                    "rango": cc_rank(bloque.complexity),
                }
            )

    promedio = sum(complejidades) / len(complejidades) if complejidades else 0.0
    maxima = max(complejidades, default=0)
    return {
        "cantidad_bloques": len(bloques),
        "promedio": promedio,
        "maxima": maxima,
        "bloques": bloques,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=Path("reportes/complejidad.json"))
    parser.add_argument("--maxima", type=int, default=20)
    parser.add_argument("--promedio", type=float, default=8.0)
    argumentos = parser.parse_args()

    raiz = Path(__file__).resolve().parents[1]
    reporte = analizar_proyecto(raiz)
    argumentos.salida.parent.mkdir(parents=True, exist_ok=True)
    argumentos.salida.write_text(
        json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"Complejidad máxima: {reporte['maxima']} (límite {argumentos.maxima})")
    print(f"Complejidad promedio: {reporte['promedio']:.2f} (límite {argumentos.promedio})")
    if reporte["maxima"] > argumentos.maxima or reporte["promedio"] > argumentos.promedio:
        raise SystemExit("La complejidad supera la política definida")


if __name__ == "__main__":
    main()
