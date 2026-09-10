from __future__ import annotations

import math
import os
from collections import defaultdict, deque
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from statistics import fmean

from algoritmos_ordenamiento import ordenar_burbuja, ordenar_quicksort
from modelos import Alerta, PerfilUsuario, Transaccion


VENTANA_RAFAGA = 60
MINIMO_RAFAGA = 5
VENTANA_REPETICION = 300
MINIMO_REPETICIONES = 3
VENTANA_UBICACIONES = 120
LIMITE_MONTO_FIJO = 1200.0


def _agrupar_por_usuario(
    transacciones: list[Transaccion],
) -> dict[str, list[Transaccion]]:
    grupos: dict[str, list[Transaccion]] = defaultdict(list)
    for transaccion in transacciones:
        grupos[transaccion.usuario].append(transaccion)
    return dict(grupos)


def _calcular_perfil(transacciones: list[Transaccion]) -> PerfilUsuario:
    montos = [transaccion.monto for transaccion in transacciones]
    promedio = fmean(montos)
    varianza = fmean((monto - promedio) ** 2 for monto in montos)
    desviacion = math.sqrt(varianza)
    limite = max(LIMITE_MONTO_FIJO, promedio + 3 * desviacion)
    return PerfilUsuario(promedio, desviacion, limite)


class CachePerfiles:
    """Cache LRU: guarda perfiles y los invalida al cargar un nuevo conjunto."""

    def __init__(self, capacidad: int = 1024) -> None:
        self._grupos: dict[str, list[Transaccion]] = {}
        self._version = 0
        self._calcular_memorizado = lru_cache(maxsize=capacidad)(self._calcular)

    def cargar(self, grupos: dict[str, list[Transaccion]]) -> None:
        self._grupos = grupos
        self._version += 1
        self._calcular_memorizado.cache_clear()

    def obtener(self, usuario: str) -> PerfilUsuario:
        return self._calcular_memorizado(usuario, self._version)

    def estadisticas(self) -> tuple[int, int]:
        info = self._calcular_memorizado.cache_info()
        return info.hits, info.misses

    def _calcular(self, usuario: str, version: int) -> PerfilUsuario:
        del version
        return _calcular_perfil(self._grupos[usuario])


def _crear_alerta(transaccion: Transaccion, tipo: str, detalle: str) -> Alerta:
    return Alerta(transaccion.id, transaccion.usuario, tipo, detalle)


def _ordenar_alertas(alertas: list[Alerta]) -> list[Alerta]:
    return sorted(alertas, key=lambda alerta: (alerta.transaccion_id, alerta.tipo))


def detectar_inicial(transacciones: list[Transaccion]) -> list[Alerta]:
    """Version inicial O(n^2): por cada operacion vuelve a recorrer listas."""
    ordenadas = ordenar_burbuja(transacciones)
    procesadas: list[Transaccion] = []
    alertas: list[Alerta] = []

    for transaccion in ordenadas:
        historial = [
            anterior
            for anterior in procesadas
            if anterior.usuario == transaccion.usuario
        ]
        todas_del_usuario = [
            candidata
            for candidata in ordenadas
            if candidata.usuario == transaccion.usuario
        ]
        perfil = _calcular_perfil(todas_del_usuario)

        if transaccion.monto > perfil.limite_monto_alto:
            alertas.append(
                _crear_alerta(
                    transaccion,
                    "MONTO_ALTO",
                    f"Monto ${transaccion.monto:.2f}, limite ${perfil.limite_monto_alto:.2f}",
                )
            )

        recientes_rafaga = [
            anterior
            for anterior in historial
            if transaccion.instante - anterior.instante <= VENTANA_RAFAGA
        ]
        if len(recientes_rafaga) + 1 >= MINIMO_RAFAGA:
            alertas.append(
                _crear_alerta(
                    transaccion,
                    "RAFAGA",
                    f"{len(recientes_rafaga) + 1} operaciones en {VENTANA_RAFAGA} segundos",
                )
            )

        repeticiones = sum(
            1
            for anterior in historial
            if transaccion.instante - anterior.instante <= VENTANA_REPETICION
            and anterior.monto == transaccion.monto
            and anterior.comercio == transaccion.comercio
        )
        if repeticiones + 1 >= MINIMO_REPETICIONES:
            alertas.append(
                _crear_alerta(
                    transaccion,
                    "OPERACION_REPETIDA",
                    f"{repeticiones + 1} operaciones iguales en 5 minutos",
                )
            )

        ubicaciones = {
            anterior.ubicacion
            for anterior in historial
            if transaccion.instante - anterior.instante <= VENTANA_UBICACIONES
        }
        ubicaciones.add(transaccion.ubicacion)
        if len(ubicaciones) >= 2:
            alertas.append(
                _crear_alerta(
                    transaccion,
                    "UBICACIONES_SIMULTANEAS",
                    f"Actividad cercana desde {', '.join(sorted(ubicaciones))}",
                )
            )

        procesadas.append(transaccion)

    return _ordenar_alertas(alertas)


def _detectar_grupo(
    transacciones: list[Transaccion],
    perfil: PerfilUsuario,
    ordenar: Callable[[list[Transaccion]], list[Transaccion]] = ordenar_quicksort,
) -> list[Alerta]:
    """Procesa un usuario en O(m), usando ventanas deslizantes."""
    grupo = ordenar(transacciones)
    ventana_rafaga: deque[Transaccion] = deque()
    ventana_repeticion: deque[Transaccion] = deque()
    ventana_ubicaciones: deque[Transaccion] = deque()
    cantidad_firmas: dict[tuple[float, str], int] = defaultdict(int)
    cantidad_ubicaciones: dict[str, int] = defaultdict(int)
    alertas: list[Alerta] = []
    emitidas: set[tuple[int, str]] = set()

    def agregar(transaccion: Transaccion, tipo: str, detalle: str) -> None:
        clave = (transaccion.id, tipo)
        if clave not in emitidas:
            emitidas.add(clave)
            alertas.append(_crear_alerta(transaccion, tipo, detalle))

    for transaccion in grupo:
        if transaccion.monto > perfil.limite_monto_alto:
            agregar(
                transaccion,
                "MONTO_ALTO",
                f"Monto ${transaccion.monto:.2f}, limite ${perfil.limite_monto_alto:.2f}",
            )

        while (
            ventana_rafaga
            and transaccion.instante - ventana_rafaga[0].instante > VENTANA_RAFAGA
        ):
            ventana_rafaga.popleft()
        ventana_rafaga.append(transaccion)
        if len(ventana_rafaga) >= MINIMO_RAFAGA:
            agregar(
                transaccion,
                "RAFAGA",
                f"{len(ventana_rafaga)} operaciones en {VENTANA_RAFAGA} segundos",
            )

        while (
            ventana_repeticion
            and transaccion.instante - ventana_repeticion[0].instante
            > VENTANA_REPETICION
        ):
            anterior = ventana_repeticion.popleft()
            firma_anterior = (anterior.monto, anterior.comercio)
            cantidad_firmas[firma_anterior] -= 1
            if cantidad_firmas[firma_anterior] == 0:
                del cantidad_firmas[firma_anterior]

        firma = (transaccion.monto, transaccion.comercio)
        ventana_repeticion.append(transaccion)
        cantidad_firmas[firma] += 1
        if cantidad_firmas[firma] >= MINIMO_REPETICIONES:
            agregar(
                transaccion,
                "OPERACION_REPETIDA",
                f"{cantidad_firmas[firma]} operaciones iguales en 5 minutos",
            )

        while (
            ventana_ubicaciones
            and transaccion.instante - ventana_ubicaciones[0].instante
            > VENTANA_UBICACIONES
        ):
            anterior = ventana_ubicaciones.popleft()
            cantidad_ubicaciones[anterior.ubicacion] -= 1
            if cantidad_ubicaciones[anterior.ubicacion] == 0:
                del cantidad_ubicaciones[anterior.ubicacion]

        ventana_ubicaciones.append(transaccion)
        cantidad_ubicaciones[transaccion.ubicacion] += 1
        if len(cantidad_ubicaciones) >= 2:
            agregar(
                transaccion,
                "UBICACIONES_SIMULTANEAS",
                "Actividad cercana desde "
                + ", ".join(sorted(cantidad_ubicaciones)),
            )

    return alertas


def detectar_con_estructuras(transacciones: list[Transaccion]) -> list[Alerta]:
    """Usa buenas estructuras, pero recalcula el perfil para cada operacion."""
    grupos = _agrupar_por_usuario(transacciones)
    alertas: list[Alerta] = []

    for grupo in grupos.values():
        # Esta repeticion simula el costo que elimina la memoizacion posterior.
        for _ in grupo:
            perfil = _calcular_perfil(grupo)
        alertas.extend(_detectar_grupo(grupo, perfil, ordenar_burbuja))

    return _ordenar_alertas(alertas)


def detectar_optimizado(
    transacciones: list[Transaccion], cache: CachePerfiles | None = None
) -> list[Alerta]:
    grupos = _agrupar_por_usuario(transacciones)
    cache_perfiles = cache or CachePerfiles()
    cache_perfiles.cargar(grupos)
    alertas: list[Alerta] = []

    for usuario, grupo in grupos.items():
        # Se consulta por cada operacion para demostrar los aciertos de cache.
        for _ in grupo:
            perfil = cache_perfiles.obtener(usuario)
        alertas.extend(_detectar_grupo(grupo, perfil))

    return _ordenar_alertas(alertas)


def _procesar_lote(
    lote: list[tuple[str, list[Transaccion]]],
) -> list[Alerta]:
    alertas: list[Alerta] = []
    for _, grupo in lote:
        alertas.extend(_detectar_grupo(grupo, _calcular_perfil(grupo)))
    return alertas


def detectar_paralelo(
    transacciones: list[Transaccion], trabajadores: int | None = None
) -> list[Alerta]:
    grupos = list(_agrupar_por_usuario(transacciones).items())
    cantidad_trabajadores = trabajadores or min(4, os.cpu_count() or 1)
    cantidad_trabajadores = max(1, min(cantidad_trabajadores, len(grupos)))

    lotes: list[list[tuple[str, list[Transaccion]]]] = [
        [] for _ in range(cantidad_trabajadores)
    ]
    for indice, grupo in enumerate(grupos):
        lotes[indice % cantidad_trabajadores].append(grupo)

    with ProcessPoolExecutor(max_workers=cantidad_trabajadores) as ejecutor:
        resultados = ejecutor.map(_procesar_lote, lotes)
        alertas = [alerta for resultado in resultados for alerta in resultado]

    return _ordenar_alertas(alertas)


def detectar_final(
    transacciones: list[Transaccion], trabajadores: int | None = None
) -> tuple[list[Alerta], str]:
    """Usa la estrategia que obtuvo menor tiempo en las mediciones."""
    del trabajadores
    return detectar_optimizado(transacciones), "secuencial optimizada"
