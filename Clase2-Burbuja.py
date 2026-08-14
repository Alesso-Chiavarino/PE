def ordenacion_burbuja(lista):
    n = len(lista)
    for i in range(n):
        for j in range(0, n-i-1):
            if lista[j] > lista[j+1]:
                lista[j], lista[j+1] = lista[j+1], lista[j]


# Ejemplo de uso
lista = list(range(10000, 0, -1))

ordenacion_burbuja(lista)

print(lista)