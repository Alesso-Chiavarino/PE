"""Pruebas del monitoreo general con psutil."""

from monitoreo import medir_recursos


def test_medir_recursos_devuelve_resultado_y_metricas() -> None:
    resultado, metricas = medir_recursos(lambda: sum(range(1000)))

    assert resultado == 499_500
    assert metricas.tiempo_segundos >= 0
    assert metricas.memoria_rss_maxima_mb > 0
    assert metricas.cpu_segundos >= 0
