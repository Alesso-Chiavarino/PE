#

import time
import random
import string

# 1. Generamos los datos de prueba (1 millón de usuarios alfanuméricos)
def generar_usuarios(cantidad):
    usuarios = []
    # Generamos un string alfanumérico aleatorio de 8 caracteres
    for _ in range(cantidad):
        usuario = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        usuarios.append(usuario)
    return usuarios

print("Generando datos de prueba (esto puede tardar unos segundos)...")
# Usamos 10 millones o 1 millón dependiendo de la RAM, 1 millón es suficiente para notar la diferencia
usuarios_lista = generar_usuarios(1000000)

# Elegimos el último elemento como objetivo para forzar el peor caso en búsquedas secuenciales
usuario_objetivo = usuarios_lista[-1] 

# 2. Preparamos las distintas estructuras de datos
usuarios_set = set(usuarios_lista)
usuarios_array = usuarios_lista.copy() # En Python las listas ya son arreglos dinámicos en memoria
usuarios_dict = {user: True for user in usuarios_lista} # Representa tanto el Diccionario como la Tabla Hash

# 3. Función para medir el tiempo de búsqueda
def medir_tiempo(estructura, nombre):
    inicio = time.perf_counter() # perf_counter es más preciso para medir tiempos cortos
    encontrado = usuario_objetivo in estructura
    fin = time.perf_counter()
    tiempo_total = fin - inicio
    print(f"{nombre:<20} | Tiempo: {tiempo_total:.8f} seg | Complejidad Promedio: {complejidades[nombre]}")

complejidades = {
    "Lista Común": "O(n)",
    "Array": "O(n)",
    "Set": "O(1)",
    "Hash/Diccionario": "O(1)"
}

print(f"\nBuscando el usuario objetivo: '{usuario_objetivo}'")
print("-" * 65)

# 4. Ejecutamos las mediciones
medir_tiempo(usuarios_lista, "Lista Común")
medir_tiempo(usuarios_array, "Array")
medir_tiempo(usuarios_set, "Set")
medir_tiempo(usuarios_dict, "Hash/Diccionario")