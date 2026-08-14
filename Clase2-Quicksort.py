def quicksort(lista):
    if len(lista) <= 1:
        return lista

    pivot = lista[len(lista) // 2]

    izquierda = [x for x in lista if x < pivot]
    centro = [x for x in lista if x == pivot]
    derecha = [x for x in lista if x > pivot]

    return quicksort(izquierda) + centro + quicksort(derecha)


# Ejemplo de uso
lista = list(range(10000, 0, -1))

print(quicksort(lista))