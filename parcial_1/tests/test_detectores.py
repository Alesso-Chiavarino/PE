import unittest

from algoritmos_ordenamiento import ordenar_burbuja, ordenar_quicksort
from detectores import (
    CachePerfiles,
    detectar_con_estructuras,
    detectar_inicial,
    detectar_optimizado,
    detectar_paralelo,
)
from generador import generar_transacciones
from medicion import ejecutar_escalabilidad
from modelos import Transaccion


class DetectoresTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.transacciones = generar_transacciones(500, semilla=7)

    def test_todas_las_versiones_encuentran_lo_mismo(self) -> None:
        inicial = detectar_inicial(self.transacciones)
        estructuras = detectar_con_estructuras(self.transacciones)
        optimizada = detectar_optimizado(self.transacciones)
        paralela = detectar_paralelo(self.transacciones, trabajadores=2)

        self.assertEqual(inicial, estructuras)
        self.assertEqual(inicial, optimizada)
        self.assertEqual(inicial, paralela)

    def test_detecta_los_cuatro_patrones(self) -> None:
        tipos = {alerta.tipo for alerta in detectar_optimizado(self.transacciones)}
        self.assertEqual(
            tipos,
            {
                "MONTO_ALTO",
                "RAFAGA",
                "OPERACION_REPETIDA",
                "UBICACIONES_SIMULTANEAS",
            },
        )

    def test_la_cache_reutiliza_perfiles(self) -> None:
        cache = CachePerfiles()
        detectar_optimizado(self.transacciones, cache)
        aciertos, fallos = cache.estadisticas()

        self.assertGreater(aciertos, 0)
        self.assertGreater(fallos, 0)
        self.assertEqual(aciertos + fallos, len(self.transacciones))

    def test_la_cache_se_invalida_con_datos_nuevos(self) -> None:
        cache = CachePerfiles()
        primer_grupo = {
            "USR-1": [Transaccion(1, "USR-1", 1, 100.0, "A", "Cordoba")]
        }
        segundo_grupo = {
            "USR-1": [
                Transaccion(1, "USR-1", 1, 100.0, "A", "Cordoba"),
                Transaccion(2, "USR-1", 2, 5000.0, "B", "Cordoba"),
            ]
        }

        cache.cargar(primer_grupo)
        perfil_anterior = cache.obtener("USR-1")
        cache.cargar(segundo_grupo)
        perfil_nuevo = cache.obtener("USR-1")

        self.assertNotEqual(perfil_anterior.promedio, perfil_nuevo.promedio)
        self.assertEqual(cache.estadisticas(), (0, 1))

    def test_burbuja_y_quicksort_ordenan_por_tiempo(self) -> None:
        tiempos_burbuja = [
            transaccion.instante for transaccion in ordenar_burbuja(self.transacciones)
        ]
        tiempos_quicksort = [
            transaccion.instante for transaccion in ordenar_quicksort(self.transacciones)
        ]

        self.assertEqual(tiempos_burbuja, sorted(tiempos_burbuja))
        self.assertEqual(tiempos_burbuja, tiempos_quicksort)

    def test_escalabilidad_compara_los_mismos_resultados(self) -> None:
        resultados = ejecutar_escalabilidad([100, 200], semilla=7)

        self.assertEqual([resultado.transacciones for resultado in resultados], [100, 200])
        self.assertTrue(all(resultado.tiempo_inicial > 0 for resultado in resultados))
        self.assertTrue(all(resultado.tiempo_optimizado > 0 for resultado in resultados))


if __name__ == "__main__":
    unittest.main()
