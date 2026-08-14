"""
Práctico 1 - Algoritmos de Búsqueda y Ordenamiento
====================================================
Objetivos:
  1. Búsqueda lineal en una lista          -> O(n)
  2. Ordenar la lista con Bubble Sort      -> O(n²)
  3. Búsqueda binaria sobre la lista ordenada -> O(log n)
  4. Medir tiempos con listas de 1.000, 10.000 y 100.000 elementos
  5. Graficar los resultados comparativos con matplotlib
"""

import random
import time
import matplotlib
matplotlib.use('Agg')  # backend sin GUI: guarda a archivo sin necesitar display
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# ──────────────────────────────────────────────────────────────────────────────
# 1. Búsqueda Lineal  O(n)
# ──────────────────────────────────────────────────────────────────────────────

def busqueda_lineal(lista: list, objetivo: int) -> int:
    """
    Recorre la lista elemento por elemento hasta encontrar el objetivo.
    Retorna el índice donde se encontró, o -1 si no existe.
    Complejidad temporal: O(n)
    """
    for i, valor in enumerate(lista):
        if valor == objetivo:
            return i
    return -1


# ──────────────────────────────────────────────────────────────────────────────
# 2. Bubble Sort  O(n²)
# ──────────────────────────────────────────────────────────────────────────────

def bubble_sort(lista: list) -> list:
    """
    Ordena la lista usando el algoritmo Bubble Sort.
    Realiza pasadas sucesivas comparando pares adyacentes y
    llevando el mayor al final en cada iteración.
    Retorna una nueva lista ordenada (no modifica la original).
    Complejidad temporal: O(n²)
    """
    arr = lista.copy()
    n = len(arr)
    for i in range(n - 1):
        intercambio = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                intercambio = True
        # Optimización: si no hubo intercambios la lista ya está ordenada
        if not intercambio:
            break
    return arr


# ──────────────────────────────────────────────────────────────────────────────
# 3. Búsqueda Binaria  O(log n)
# ──────────────────────────────────────────────────────────────────────────────

def busqueda_binaria(lista_ordenada: list, objetivo: int) -> int:
    """
    Busca el objetivo en una lista ORDENADA dividiendo el espacio de búsqueda
    a la mitad en cada paso.
    Retorna el índice donde se encontró, o -1 si no existe.
    Complejidad temporal: O(log n)
    Precondición: la lista debe estar ordenada de forma ascendente.
    """
    izq, der = 0, len(lista_ordenada) - 1

    while izq <= der:
        medio = (izq + der) // 2
        if lista_ordenada[medio] == objetivo:
            return medio
        elif lista_ordenada[medio] < objetivo:
            izq = medio + 1
        else:
            der = medio - 1

    return -1


# ──────────────────────────────────────────────────────────────────────────────
# 4. Benchmark: medir tiempos
# ──────────────────────────────────────────────────────────────────────────────

def medir_tiempos(tamanios: list) -> dict:
    """
    Para cada tamaño de lista:
      - Genera una lista aleatoria
      - Mide el tiempo de búsqueda lineal
      - Mide el tiempo de Bubble Sort
      - Mide el tiempo de búsqueda binaria (sobre la lista ya ordenada)
    Retorna un diccionario con los resultados.
    """
    resultados = {
        "tamanios": tamanios,
        "lineal": [],
        "bubble_sort": [],
        "binaria": [],
    }

    for n in tamanios:
        # Lista aleatoria de enteros entre 0 y n*10
        lista = random.sample(range(n * 10), n)

        # El objetivo a buscar: uno que existe en la lista (worst-case: el último)
        objetivo = lista[-1]

        # ── Búsqueda lineal ──────────────────────────────────────────────────
        inicio = time.perf_counter()
        busqueda_lineal(lista, objetivo)
        resultados["lineal"].append(time.perf_counter() - inicio)

        # ── Bubble Sort ──────────────────────────────────────────────────────
        inicio = time.perf_counter()
        lista_ordenada = bubble_sort(lista)
        resultados["bubble_sort"].append(time.perf_counter() - inicio)

        # ── Búsqueda binaria (sobre la lista ya ordenada) ────────────────────
        objetivo_ordenado = lista_ordenada[n // 2]   # elemento del medio
        inicio = time.perf_counter()
        busqueda_binaria(lista_ordenada, objetivo_ordenado)
        resultados["binaria"].append(time.perf_counter() - inicio)

        print(
            f"  n={n:>8,} | lineal={resultados['lineal'][-1]*1e6:>10.2f} us"
            f" | bubble_sort={resultados['bubble_sort'][-1]*1e3:>10.4f} ms"
            f" | binaria={resultados['binaria'][-1]*1e6:>8.4f} us"
        )

    return resultados


# ──────────────────────────────────────────────────────────────────────────────
# 5. Graficar con matplotlib
# ──────────────────────────────────────────────────────────────────────────────

def graficar(resultados: dict) -> None:
    """
    Genera dos subgráficos comparando los tiempos de ejecución de cada
    algoritmo para los distintos tamaños de lista.
    """
    tamanios = resultados["tamanios"]
    etiquetas = [f"{n:,}" for n in tamanios]

    t_lineal  = [t * 1e3 for t in resultados["lineal"]]       # ms
    t_bubble  = [t * 1e3 for t in resultados["bubble_sort"]]  # ms
    t_binaria = [t * 1e6 for t in resultados["binaria"]]      # us

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        "Comparacion de Algoritmos de Busqueda y Ordenamiento\n"
        "Practico 1 - Programacion de Estructuras",
        fontsize=14, fontweight="bold"
    )

    x = list(range(len(tamanios)))
    ancho = 0.35

    # ── Gráfico 1: Búsqueda Lineal vs Bubble Sort (en ms) ───────────────────
    barras_lineal = ax1.bar(
        [i - ancho / 2 for i in x], t_lineal, ancho,
        label="Busqueda Lineal  O(n)", color="#4C72B0", alpha=0.85
    )
    barras_bubble = ax1.bar(
        [i + ancho / 2 for i in x], t_bubble, ancho,
        label="Bubble Sort  O(n^2)", color="#DD8452", alpha=0.85
    )

    ax1.set_title("Busqueda Lineal vs Bubble Sort")
    ax1.set_xlabel("Cantidad de elementos")
    ax1.set_ylabel("Tiempo (ms)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(etiquetas)
    ax1.legend()
    ax1.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.4f"))
    ax1.bar_label(barras_lineal, fmt="%.4f", padding=3, fontsize=8)
    ax1.bar_label(barras_bubble, fmt="%.4f", padding=3, fontsize=8)
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    # ── Gráfico 2: Búsqueda Binaria (en µs) ─────────────────────────────────
    barras_binaria = ax2.bar(
        x, t_binaria, ancho * 1.4,
        label="Busqueda Binaria  O(log n)", color="#55A868", alpha=0.85
    )

    ax2.set_title("Busqueda Binaria")
    ax2.set_xlabel("Cantidad de elementos")
    ax2.set_ylabel("Tiempo (us)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(etiquetas)
    ax2.legend()
    ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.4f"))
    ax2.bar_label(barras_binaria, fmt="%.4f", padding=3, fontsize=8)
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig("resultados_practico1.png", dpi=150, bbox_inches="tight")
    print("\n  Grafico guardado como 'resultados_practico1.png'")


# ──────────────────────────────────────────────────────────────────────────────
# Punto de entrada
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    TAMANIOS = [1_000, 10_000, 100_000]

    print("=" * 70)
    print("  Practico 1 - Algoritmos de Busqueda y Ordenamiento")
    print("=" * 70)

    # Demostración rápida con una lista pequeña
    demo = [random.randint(1, 50) for _ in range(10)]
    objetivo_demo = demo[random.randint(0, 9)]
    demo_ord = bubble_sort(demo)

    print(f"\n  [Demo] Lista original : {demo}")
    print(f"         Lista ordenada : {demo_ord}")
    print(f"         Objetivo       : {objetivo_demo}")
    idx_lineal  = busqueda_lineal(demo, objetivo_demo)
    idx_binaria = busqueda_binaria(demo_ord, objetivo_demo)
    print(f"         Busqueda lineal  -> indice {idx_lineal}")
    print(f"         Busqueda binaria (lista ordenada) -> indice {idx_binaria}")

    print(f"\n  Midiendo tiempos para n = {TAMANIOS} ...\n")
    resultados = medir_tiempos(TAMANIOS)

    print("\n  Generando grafico ...")
    graficar(resultados)

    print("\n" + "=" * 70)
    print("  Conclusion:")
    print("    - Busqueda lineal  crece linealmente con n           -> O(n)")
    print("    - Bubble Sort      crece cuadraticamente con n       -> O(n^2)")
    print("    - Busqueda binaria crece de forma logaritmica con n  -> O(log n)")
    print("=" * 70)
