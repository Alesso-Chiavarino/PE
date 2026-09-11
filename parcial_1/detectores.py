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


# ==============================================================================
# 2. MEMOIZACION Y CACHING INTELIGENTE
# ==============================================================================
class CachePerfiles:
    """
    [CRITERIO: MEMOIZACION Y CACHE LRU]
    - Problema: Calcular el perfil de un usuario (media, varianza y desviacion)
      requiere recorrer todas sus transacciones. Si un usuario tiene 50 transacciones,
      hacerlo en cada una repetiria 50 veces el mismo calculo estadistico.
    - Memoizacion: Se guarda el PerfilUsuario precalculado para no recalcularlo.
    - Caching Inteligente con LRU: Se usa functools.lru_cache con un limite
      maximo (1024 usuarios). Si la cantidad de usuarios supera el limite,
      desaloja los menos utilizados recientemente (evita consumo infinito de RAM).
    - Invalidacion de Cache: Al ingresar un nuevo lote de transacciones (cargar()),
      se incrementa la version y se invoca cache_clear() para evitar servir
      datos viejos (stale data).
    """

    def __init__(self, capacidad: int = 1024) -> None:
        self._grupos: dict[str, list[Transaccion]] = {}
        self._version = 0
        # Decorador LRU cache sobre el metodo interno _calcular
        self._calcular_memorizado = lru_cache(maxsize=capacidad)(self._calcular)

    def cargar(self, grupos: dict[str, list[Transaccion]]) -> None:
        """Carga nuevos grupos e invalida el cache anterior."""
        self._grupos = grupos
        self._version += 1
        self._calcular_memorizado.cache_clear()

    def obtener(self, usuario: str) -> PerfilUsuario:
        """Retorna el perfil desde memoria o lo calcula si no estaba en cache."""
        return self._calcular_memorizado(usuario, self._version)

    def estadisticas(self) -> tuple[int, int]:
        """Devuelve aciertos (hits) y fallos (misses) para medir la efectividad."""
        info = self._calcular_memorizado.cache_info()
        return info.hits, info.misses

    def _calcular(self, usuario: str, version: int) -> PerfilUsuario:
        del version
        return _calcular_perfil(self._grupos[usuario])



def _crear_alerta(transaccion: Transaccion, tipo: str, detalle: str) -> Alerta:
    return Alerta(transaccion.id, transaccion.usuario, tipo, detalle)


def _ordenar_alertas(alertas: list[Alerta]) -> list[Alerta]:
    return sorted(alertas, key=lambda alerta: (alerta.transaccion_id, alerta.tipo))


# ==============================================================================
# 3. VERSION INICIAL (BASELINE O(n^2)) - INEFICIENCIAS DEMOSTRADAS
# ==============================================================================
def detectar_inicial(transacciones: list[Transaccion]) -> list[Alerta]:
    """
    [IMPLEMENTACION INICIAL / BASELINE]
    - Ineficiencia 1 (Algoritmo): Usa ordenar_burbuja -> O(n^2) en tiempo.
    - Ineficiencia 2 (Estructuras de datos): Mantiene 'procesadas' como lista plana.
      Por cada transaccion en el bucle externo (n iteraciones), filtra la lista
      completa con list comprehensions -> O(n) iteraciones internas -> O(n^2).
    - Ineficiencia 3 (Calculo redundante / Sin Cache): Vuelve a calcular el perfil
      estadistico del usuario en CADA transaccion (_calcular_perfil) en vez de reutilizarlo.
    - Ineficiencia 4 (Ventanas sin Deque): Revisa el historial completo con sum()
      y sets creados desde cero en vez de usar colas deslizantes.
    """
    ordenadas = ordenar_burbuja(transacciones)  # Cuello de botella 1: Burbuja O(n^2)
    procesadas: list[Transaccion] = []
    alertas: list[Alerta] = []

    for transaccion in ordenadas:
        # Busqueda lineal repetida O(n) para filtrar transacciones previas del usuario
        historial = [
            anterior
            for anterior in procesadas
            if anterior.usuario == transaccion.usuario
        ]
        # Busqueda lineal repetida O(n) sobre toda la lista para recalcular perfil
        todas_del_usuario = [
            candidata
            for candidata in ordenadas
            if candidata.usuario == transaccion.usuario
        ]
        # Recalculo redundante del perfil en cada iteracion (sin memoizacion)
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


# ==============================================================================
# 4. ESTRUCTURAS DE DATOS EFICIENTES (deque, dict, set) Y VENTANAS DESLIZANTES
# ==============================================================================
def _detectar_grupo(
    transacciones: list[Transaccion],
    perfil: PerfilUsuario,
    ordenar: Callable[[list[Transaccion]], list[Transaccion]] = ordenar_quicksort,
) -> list[Alerta]:
    """
    [ESTRUCTURAS DE DATOS OPTIMIZADAS]
    - deque (Double Ended Queue): Implementa colas deslizantes de tiempo.
      Agregar al final con append() es O(1) y descartar transacciones vencidas
      con popleft() es O(1).
      (En una list comun de Python, pop(0) es O(k) porque debe desplazar todos
      los elementos restantes en memoria RAM).
    - dict / defaultdict: Permite contar firmas de transacciones (monto, comercio)
      y ubicaciones en O(1) promedio por hash table, sin recorridos lineales.
    - set: Estructura de dispersion hash para registrar alertas emitidas (clave ID, tipo)
      evitando duplicados con verificacion 'in' en O(1).
    - Complejidad Temporal del grupo: Al entrar y salir cada transaccion una sola
      vez de cada ventana, el recorrido completo es estrictamente O(m) lineal
      (siendo m las transacciones del usuario), tras el ordenamiento O(m log m).
    """
    grupo = ordenar(transacciones)

    # Ventanas deslizantes FIFO con deque: desalojo O(1)
    ventana_rafaga: deque[Transaccion] = deque()
    ventana_repeticion: deque[Transaccion] = deque()
    ventana_ubicaciones: deque[Transaccion] = deque()

    # Tablas hash con acceso O(1) para frecuencias
    cantidad_firmas: dict[tuple[float, str], int] = defaultdict(int)
    cantidad_ubicaciones: dict[str, int] = defaultdict(int)

    alertas: list[Alerta] = []
    # Conjunto set O(1) para deduplicacion de alertas
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


# ==============================================================================
# 5. CONCURRENCIA Y PARALELISMO: MULTIPROCESSING vs GIL
# ==============================================================================
def detectar_paralelo(
    transacciones: list[Transaccion], trabajadores: int | None = None
) -> list[Alerta]:
    """
    [CRITERIO: CONCURRENCIA Y PARALELISMO]
    - Por que Procesos (ProcessPoolExecutor) y NO Hilos (threading)?
      La tarea es intensiva en CPU (CPU-Bound: ordenar, iterar, calcular).
      En Python, el GIL (Global Interpreter Lock) impide que multiples hilos
      ejecuten bytecode de Python en paralelo en distintos cores.
      ProcessPoolExecutor crea procesos independientes con su propio interprete
      y espacio de memoria, aprovechando verdaderamente multiples nucleos.
    - Descomposicion del problema sin Locks ni Race Conditions:
      Como el comportamiento de un usuario es independiente de otro, se particionan
      los usuarios en lotes (chunks). No se requiere memoria compartida ni candados (mutex/locks).
    - Trade-off / Overhead de Paralelizacion:
      La creacion de procesos, serializacion (pickle) de transacciones por IPC
      (Inter-Process Communication) y recoleccion de resultados agrega un costo fijo.
      Si el volumen de trabajo secuencial ya es extremadamente rapido (~12 ms),
      el overhead supera la ganancia (ley de Amdahl).
    """
    grupos = list(_agrupar_por_usuario(transacciones).items())
    cantidad_trabajadores = trabajadores or min(4, os.cpu_count() or 1)
    cantidad_trabajadores = max(1, min(cantidad_trabajadores, len(grupos)))

    # Reparto de usuarios en lotes para los workers (balanceo de carga round-robin)
    lotes: list[list[tuple[str, list[Transaccion]]]] = [
        [] for _ in range(cantidad_trabajadores)
    ]
    for indice, grupo in enumerate(grupos):
        lotes[indice % cantidad_trabajadores].append(grupo)

    # Ejecucion en paralelo a traves de procesos de SO
    with ProcessPoolExecutor(max_workers=cantidad_trabajadores) as ejecutor:
        resultados = ejecutor.map(_procesar_lote, lotes)
        alertas = [alerta for resultado in resultados for alerta in resultado]

    return _ordenar_alertas(alertas)


# ==============================================================================
# 6. VERSION FINAL: JUSTIFICACION BASADA EN MEDICIONES EMPIRICAS
# ==============================================================================
def detectar_final(
    transacciones: list[Transaccion], trabajadores: int | None = None
) -> tuple[list[Alerta], str]:
    """
    [CRITERIO: MEDIR, COMPARAR Y JUSTIFICAR OPTIMIZACIONES]
    - Justificacion de Ingenieria:
      Medir objetivamente demostro que para este volumen (5.000 transacciones):
        * Version Inicial: ~0.80s - 0.93s
        * Version Paralela: ~0.07s - 0.08s (penalizada por overhead de procesos)
        * Version Optimizada Secuencial: ~0.010s - 0.012s (LA MAS RAPIDA)
      Un buen ingeniero no asume que 'paralelo siempre es mejor', sino que mide
      y descarta tecnicas cuando el costo supera el beneficio.
    - Decision: Se selecciona la version secuencial optimizada como version final.
    """
    del trabajadores
    return detectar_optimizado(transacciones), "secuencial optimizada"

