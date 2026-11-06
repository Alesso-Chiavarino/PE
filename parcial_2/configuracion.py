"""Configuracion central del detector de transacciones."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConfiguracionDeteccion:
    """Agrupa los umbrales utilizados por las reglas de deteccion."""

    ventana_rafaga: int = 60
    minimo_rafaga: int = 5
    ventana_repeticion: int = 300
    minimo_repeticiones: int = 3
    ventana_ubicaciones: int = 120
    limite_monto_fijo: float = 1200.0


CONFIGURACION_PREDETERMINADA = ConfiguracionDeteccion()
