from modelos import Transaccion


# ==============================================================================
# 1. ANALISIS DE COMPLEJIDAD Y SELECCION DE ALGORITMOS: BURBUJA vs QUICKSORT
# ==============================================================================

def ordenar_burbuja(transacciones: list[Transaccion]) -> list[Transaccion]:
    """
    [ALGORITMO INICIAL / BASELINE]
    - Tecnica: Comparacion e intercambio de elementos vecinos adyacentes.
    - Complejidad Temporal: O(n^2) en el peor y caso promedio.
      Realiza (n - 1) + (n - 2) + ... + 1 = n(n - 1)/2 comparaciones.
    - Impacto: Al duplicar las transacciones, el tiempo se cuadruplica.
      Inviable para grandes volumenes de transacciones financieras.
    """
    resultado = transacciones.copy()
    cantidad = len(resultado)

    for pasada in range(cantidad - 1):
        for posicion in range(cantidad - pasada - 1):
            actual = resultado[posicion]
            siguiente = resultado[posicion + 1]
            if actual.instante > siguiente.instante:
                # Intercambio in-place de elementos vecinos
                resultado[posicion], resultado[posicion + 1] = siguiente, actual

    return resultado


def ordenar_quicksort(transacciones: list[Transaccion]) -> list[Transaccion]:
    """
    [ALGORITMO OPTIMIZADO / SELECCIONADO]
    - Tecnica: Divide y Venceras (Divide and Conquer).
    - Complejidad Temporal: O(n log n) en promedio.
      En cada nivel se particionan n elementos en log2(n) niveles de recursion.
    - Seleccion de Pivote: Se toma el elemento central (len // 2) para mitigar
      el peor caso O(n^2) en listas que ya vengan parcialmente ordenadas.
    - Justificacion: El ordenamiento cronologico es obligatorio para analizar
      ventanas temporales (60s, 120s, 300s). Quicksort reduce el tiempo de ordenamiento
      de cientos de milisegundos a pocos milisegundos en 5.000 transacciones.
    """
    if len(transacciones) <= 1:
        return transacciones.copy()

    # Seleccion del pivote en la posicion central
    pivote = transacciones[len(transacciones) // 2].instante
    menores = [t for t in transacciones if t.instante < pivote]
    iguales = [t for t in transacciones if t.instante == pivote]
    mayores = [t for t in transacciones if t.instante > pivote]

    # Recursion sobre subconjuntos particionados
    return ordenar_quicksort(menores) + iguales + ordenar_quicksort(mayores)
