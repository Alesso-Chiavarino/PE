Seguridad
=========

Controles
---------

Bandit analiza patrones inseguros en el código Python. El pipeline bloquea
hallazgos de severidad media o alta y genera ``bandit.json``. pip-audit compara las
dependencias de ejecución con vulnerabilidades conocidas y genera
``pip-audit.json``. detect-secrets compara el repositorio con
``.secrets.baseline`` y rechaza secretos nuevos.

Política de severidad
---------------------

* Severidad crítica o alta confirmada: bloquea la integración.
* Severidad media: bloquea hasta ser corregida o documentada como excepción.
* Severidad baja: se revisa y puede aceptarse con justificación.
* Secretos confirmados: siempre bloquean y deben revocarse antes de eliminarlos.

Falsos positivos conocidos
--------------------------

Bandit B311 marca ``random.Random`` porque no es un generador criptográfico. El
proyecto lo utiliza únicamente para fabricar datos simulados y repetibles, no para
contraseñas, tokens ni decisiones de seguridad. Por eso el hallazgo bajo se acepta;
los niveles medio y alto continúan siendo bloqueantes.

Dependencias
------------

Las versiones directas están fijadas en ``requirements.txt`` y
``requirements-dev.txt``. ``requirements-lock.txt`` fija además las dependencias
transitivas y es el archivo que instala el CI. Dependabot revisa semanalmente
dependencias Python y acciones de GitHub. Una actualización debe atravesar todos
los controles del CI y actualizar el archivo de bloqueo.
