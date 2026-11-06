Mantenimiento e integración continua
=====================================

Flujo de contribución
---------------------

Cada cambio se realiza en una rama y se integra mediante un pull request. GitHub
Actions ejecuta automáticamente los controles ante cada push y cada pull request
hacia ``main``. No debe integrarse código mientras exista un control bloqueante.

Preparación local
-----------------

::

   python -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements-lock.txt

Controles equivalentes al CI
----------------------------

::

   python -m ruff check .
   python -m mypy algoritmos_ordenamiento.py archivos.py configuracion.py detectores.py generador.py main.py medicion.py modelos.py monitoreo.py perfilado.py interfaz tests scripts
   python -m scripts.verificar_complejidad
   python -m pytest --cov --cov-fail-under=90
   python -m bandit -r . -x ./.venv,./tests,./docs,./presentacion,./resultados -ll
   python -m pip_audit -r requirements.txt --cache-dir reportes/.pip-audit-cache
   detect-secrets scan --all-files --baseline .secrets.baseline
   git diff --exit-code --ignore-matching-lines='"generated_at":' .secrets.baseline
   python -m sphinx -W --keep-going -b html docs docs/_build/html
   python -m scripts.verificar_rendimiento
   python -m scripts.verificar_memoria

Resolución de fallos
--------------------

Ruff o mypy
   Corregir el archivo y la línea informados. No ignorar errores sin justificarlo.

pytest o cobertura
   Reproducir localmente la prueba. Agregar pruebas si la cobertura queda debajo
   del umbral.

Bandit, pip-audit o secretos
   Revisar la severidad, actualizar la dependencia o retirar y revocar el secreto.
   Toda excepción debe registrarse en :doc:`seguridad`.

Sphinx
   Ejecutar el comando con ``-W`` y corregir la advertencia o el enlace roto.

Rendimiento o memoria
   Repetir la medición en condiciones equivalentes, revisar el reporte JSON y
   comparar el cambio con la línea base del pull request.
