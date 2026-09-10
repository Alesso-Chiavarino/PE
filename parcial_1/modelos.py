from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Transaccion:
    id: int
    usuario: str
    instante: int
    monto: float
    comercio: str
    ubicacion: str


@dataclass(frozen=True, slots=True)
class Alerta:
    transaccion_id: int
    usuario: str
    tipo: str
    detalle: str


@dataclass(frozen=True, slots=True)
class PerfilUsuario:
    promedio: float
    desviacion: float
    limite_monto_alto: float

