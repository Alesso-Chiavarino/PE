"""Configuracion de Sphinx para el segundo parcial."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

project = "Detector de transacciones sospechosas"
author = "Programacion Eficiente"
release = "2.0"

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]
templates_path = ["_templates"]
exclude_patterns = ["_build"]
html_theme = "alabaster"
language = "es"
