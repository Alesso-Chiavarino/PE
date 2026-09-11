def fibonacci_iterativo(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# Ejemplo de uso
print(fibonacci_iterativo(40))  # Salida: 102334155