# Cambios del tercer parcial

## Objetivo

El tercer parcial no reemplaza el detector construido anteriormente. Convierte
los controles manuales del segundo parcial en un proceso automático, reproducible
y bloqueante antes de integrar cambios.

## Antes y después

| Tema | Antes | Tercer parcial |
|---|---|---|
| Ejecución de controles | Cada herramienta se corría manualmente | GitHub Actions ejecuta cinco trabajos ante push y pull request |
| Calidad estática | flake8 sin política de CI | Ruff y mypy bloquean errores de estilo, código y tipos |
| Complejidad | Se explicaba teóricamente | Radon genera JSON y aplica máximo 20, promedio 8 |
| Pruebas | 15 pruebas pytest | Las mismas pruebas bloquean el CI y exigen cobertura mínima del 90 % |
| Seguridad | Sin análisis automático | Bandit, pip-audit y detect-secrets con política de severidad |
| Dependencias | Rangos con `>=` | Versiones directas y transitivas fijadas |
| Rendimiento | Benchmark ejecutado a mano | Comparación repetida con mediana y criterio de regresión |
| Memoria | Medición informativa | Control reproducible con límite de 25 MiB |
| Profiling | cProfile y SnakeViz locales | El CI genera y conserva los archivos `.prof` |
| Documentación | Cuatro páginas Sphinx | Diez páginas con arquitectura, diseño, pruebas, seguridad y mantenimiento |
| Publicación | Documentación solamente local | Sitio Sphinx publicado automáticamente con GitHub Pages |

## Pipeline

El archivo `.github/workflows/ci.yml` define cinco trabajos:

1. **Calidad estática:** Ruff, mypy y complejidad.
2. **Pruebas:** pytest, cobertura XML y resultados JUnit.
3. **Seguridad:** código, dependencias y secretos.
4. **Documentación:** sitio Sphinx y validación de enlaces.
5. **Rendimiento:** benchmark, memoria y profiling, después de los controles rápidos.

Cada trabajo guarda reportes como artefactos para que el resultado pueda revisarse
sin repetir la ejecución.

## Cambios mínimos en el código existente

El algoritmo principal no fue reescrito. Se eliminó un comentario inválido que
hacía fallar el linter, se ordenaron imports automáticamente y se reemplazó una
lambda de la interfaz por una llamada tipable por mypy. Los demás cambios están en
configuración, scripts de control, documentación y CI.

## Resultados de la línea base

- 15 pruebas aprobadas.
- 93,82 % de cobertura total en los módulos principales.
- complejidad máxima 18 y promedio 2,56;
- versión optimizada aproximadamente 70 veces más rápida que la inicial en 2.500 transacciones;
- 8,35 MiB de memoria Python al procesar 20.000 transacciones por lotes;
- ninguna vulnerabilidad conocida en las dependencias de ejecución;
- documentación Sphinx y validación de enlaces sin advertencias.

Los tiempos exactos pueden cambiar según el equipo. Por eso el benchmark compara
ambas versiones dentro de la misma ejecución y utiliza la mediana de tres intentos.
