"""Lectura, escritura y deteccion sobre archivos CSV grandes."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

from configuracion import CONFIGURACION_PREDETERMINADA
from detectores import EstadoDeteccionUsuario
from modelos import Alerta, PerfilUsuario, Transaccion


CAMPOS_TRANSACCION = (
    "id",
    "usuario",
    "instante",
    "monto",
    "comercio",
    "ubicacion",
)
CAMPOS_ALERTA = ("transaccion_id", "usuario", "tipo", "detalle")
TAMANIO_BUFFER_PREDETERMINADO = 1024 * 1024


@dataclass(slots=True)
class AcumuladorPerfil:
    """Calcula promedio y varianza incremental con memoria constante."""

    cantidad: int = 0
    promedio: float = 0.0
    suma_desviaciones: float = 0.0

    def agregar(self, monto: float) -> None:
        self.cantidad += 1
        diferencia = monto - self.promedio
        self.promedio += diferencia / self.cantidad
        diferencia_final = monto - self.promedio
        self.suma_desviaciones += diferencia * diferencia_final

    def convertir(self) -> PerfilUsuario:
        varianza = self.suma_desviaciones / self.cantidad
        desviacion = math.sqrt(max(varianza, 0.0))
        limite = max(
            CONFIGURACION_PREDETERMINADA.limite_monto_fijo,
            self.promedio + 3 * desviacion,
        )
        return PerfilUsuario(self.promedio, desviacion, limite)


def guardar_transacciones_csv(
    transacciones: Iterable[Transaccion],
    ruta: Path,
    tamanio_buffer: int = TAMANIO_BUFFER_PREDETERMINADO,
) -> int:
    """Escribe transacciones progresivamente en un CSV bufferizado."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    cantidad = 0
    with ruta.open(
        "w", newline="", encoding="utf-8", buffering=tamanio_buffer
    ) as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(CAMPOS_TRANSACCION)
        for transaccion in transacciones:
            escritor.writerow(
                (
                    transaccion.id,
                    transaccion.usuario,
                    transaccion.instante,
                    transaccion.monto,
                    transaccion.comercio,
                    transaccion.ubicacion,
                )
            )
            cantidad += 1
    return cantidad


def leer_transacciones_csv(
    ruta: Path,
    tamanio_buffer: int = TAMANIO_BUFFER_PREDETERMINADO,
) -> Iterator[Transaccion]:
    """Entrega una transaccion por vez sin cargar el archivo completo."""
    with ruta.open("r", newline="", encoding="utf-8", buffering=tamanio_buffer) as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != list(CAMPOS_TRANSACCION):
            raise ValueError(
                "El CSV debe contener las columnas: " + ", ".join(CAMPOS_TRANSACCION)
            )
        for numero_fila, fila in enumerate(lector, start=2):
            try:
                yield Transaccion(
                    id=int(fila["id"]),
                    usuario=fila["usuario"],
                    instante=int(fila["instante"]),
                    monto=float(fila["monto"]),
                    comercio=fila["comercio"],
                    ubicacion=fila["ubicacion"],
                )
            except (TypeError, ValueError) as error:
                raise ValueError(f"Datos invalidos en la fila {numero_fila}") from error


def agrupar_en_lotes(
    elementos: Iterable[Transaccion], tamanio_lote: int
) -> Iterator[list[Transaccion]]:
    """Agrupa un iterable en listas de tamaño limitado."""
    if tamanio_lote <= 0:
        raise ValueError("El tamaño del lote debe ser mayor que cero")

    lote: list[Transaccion] = []
    for elemento in elementos:
        lote.append(elemento)
        if len(lote) == tamanio_lote:
            yield lote
            lote = []
    if lote:
        yield lote


def calcular_perfiles_csv(ruta: Path) -> tuple[dict[str, PerfilUsuario], int]:
    """Primera pasada del archivo para calcular los perfiles por usuario."""
    acumuladores: dict[str, AcumuladorPerfil] = defaultdict(AcumuladorPerfil)
    cantidad = 0
    for transaccion in leer_transacciones_csv(ruta):
        acumuladores[transaccion.usuario].agregar(transaccion.monto)
        cantidad += 1
    perfiles = {
        usuario: acumulador.convertir()
        for usuario, acumulador in acumuladores.items()
    }
    return perfiles, cantidad


def iterar_alertas_csv(ruta: Path, tamanio_lote: int = 10_000) -> Iterator[Alerta]:
    """Detecta alertas en dos pasadas y conserva estado entre lotes."""
    perfiles, _ = calcular_perfiles_csv(ruta)
    estados = {
        usuario: EstadoDeteccionUsuario(perfil)
        for usuario, perfil in perfiles.items()
    }
    ultimo_instante = -1

    for lote in agrupar_en_lotes(leer_transacciones_csv(ruta), tamanio_lote):
        for transaccion in lote:
            if transaccion.instante < ultimo_instante:
                raise ValueError(
                    "El archivo debe estar ordenado por la columna instante"
                )
            ultimo_instante = transaccion.instante
            alertas = estados[transaccion.usuario].procesar(transaccion)
            yield from sorted(alertas, key=lambda alerta: alerta.tipo)


def guardar_alertas_csv(
    alertas: Iterable[Alerta],
    ruta: Path,
    tamanio_buffer: int = TAMANIO_BUFFER_PREDETERMINADO,
) -> int:
    """Escribe alertas progresivamente y devuelve la cantidad generada."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    cantidad = 0
    with ruta.open(
        "w", newline="", encoding="utf-8", buffering=tamanio_buffer
    ) as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(CAMPOS_ALERTA)
        for alerta in alertas:
            escritor.writerow(
                (
                    alerta.transaccion_id,
                    alerta.usuario,
                    alerta.tipo,
                    alerta.detalle,
                )
            )
            cantidad += 1
    return cantidad
