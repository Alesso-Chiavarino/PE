import random

from modelos import Transaccion


UBICACIONES = ("Cordoba", "Rosario", "Mendoza", "Buenos Aires")
COMERCIOS = ("Supermercado", "Farmacia", "Combustible", "Restaurante", "Tienda")
CANTIDAD_ANOMALIAS = 12


def generar_transacciones(cantidad: int, semilla: int = 42) -> list[Transaccion]:
    """Genera datos repetibles e incluye los cuatro patrones sospechosos."""
    if cantidad < 100:
        raise ValueError("La cantidad minima es 100 transacciones")

    aleatorio = random.Random(semilla)
    cantidad_usuarios = max(20, cantidad // 50)
    usuarios = [f"USR-{numero:04d}" for numero in range(cantidad_usuarios)]
    ubicacion_usuario = {
        usuario: aleatorio.choice(UBICACIONES) for usuario in usuarios
    }

    transacciones: list[Transaccion] = []
    instante = 0

    for identificador in range(1, cantidad - CANTIDAD_ANOMALIAS + 1):
        instante += aleatorio.randint(1, 3)
        usuario = aleatorio.choice(usuarios)
        transacciones.append(
            Transaccion(
                id=identificador,
                usuario=usuario,
                instante=instante,
                monto=round(aleatorio.uniform(10, 500), 2),
                comercio=aleatorio.choice(COMERCIOS),
                ubicacion=ubicacion_usuario[usuario],
            )
        )

    siguiente_id = len(transacciones) + 1
    usuario_anomalo = "USR-ANOMALO"

    # Un monto muy superior a los montos normales.
    transacciones.append(
        Transaccion(siguiente_id, usuario_anomalo, instante + 10, 8000.0, "Tienda", "Cordoba")
    )
    siguiente_id += 1

    # Seis operaciones en menos de un minuto.
    for numero in range(6):
        transacciones.append(
            Transaccion(
                siguiente_id,
                usuario_anomalo,
                instante + 30 + numero * 5,
                100.0 + numero,
                "Kiosco",
                "Cordoba",
            )
        )
        siguiente_id += 1

    # Tres operaciones iguales en una ventana de cinco minutos.
    for numero in range(3):
        transacciones.append(
            Transaccion(
                siguiente_id,
                usuario_anomalo,
                instante + 100 + numero * 10,
                777.77,
                "Electronica",
                "Cordoba",
            )
        )
        siguiente_id += 1

    # Dos compras casi simultaneas en ciudades diferentes.
    transacciones.extend(
        [
            Transaccion(siguiente_id, usuario_anomalo, instante + 180, 80.0, "Cafe", "Cordoba"),
            Transaccion(siguiente_id + 1, usuario_anomalo, instante + 185, 90.0, "Cafe", "Madrid"),
        ]
    )

    # Simula operaciones recibidas desde distintas fuentes y fuera de orden.
    aleatorio.shuffle(transacciones)
    return transacciones
