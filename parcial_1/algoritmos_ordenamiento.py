from modelos import Transaccion


def ordenar_burbuja(transacciones: list[Transaccion]) -> list[Transaccion]:
    """Ordena por tiempo comparando elementos vecinos. Complejidad O(n^2)."""
    resultado = transacciones.copy()
    cantidad = len(resultado)

    for pasada in range(cantidad - 1):
        for posicion in range(cantidad - pasada - 1):
            actual = resultado[posicion]
            siguiente = resultado[posicion + 1]
            if actual.instante > siguiente.instante:
                resultado[posicion], resultado[posicion + 1] = siguiente, actual

    return resultado


def ordenar_quicksort(transacciones: list[Transaccion]) -> list[Transaccion]:
    """Ordena por tiempo dividiendo la lista. Promedio O(n log n)."""
    if len(transacciones) <= 1:
        return transacciones.copy()

    pivote = transacciones[len(transacciones) // 2].instante
    menores = [t for t in transacciones if t.instante < pivote]
    iguales = [t for t in transacciones if t.instante == pivote]
    mayores = [t for t in transacciones if t.instante > pivote]

    return ordenar_quicksort(menores) + iguales + ordenar_quicksort(mayores)

