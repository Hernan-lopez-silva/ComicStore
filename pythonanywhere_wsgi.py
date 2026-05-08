"""
WSGI config para PythonAnywhere.

Reemplaza el contenido del archivo WSGI que genera PythonAnywhere
con este archivo, ajustando MY_USERNAME y PROJECT_DIR según corresponda.
"""
import sys
import os

# ── Ajusta estas dos variables ──────────────────────────────────────────────
MY_USERNAME    = 'TU_USUARIO_PYTHONANYWHERE'   # ej: 'hernanlsilva'
PROJECT_FOLDER = 'ComicStore'                   # nombre de la carpeta del repo
# ────────────────────────────────────────────────────────────────────────────

PROJECT_DIR = f'/home/{MY_USERNAME}/{PROJECT_FOLDER}'

# Agregar el proyecto al path de Python
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Variables de entorno necesarias para producción
os.environ['DJANGO_SETTINGS_MODULE'] = 'comicstore.settings'
os.environ['PYTHONANYWHERE_DOMAIN'] = f'{MY_USERNAME}.pythonanywhere.com'
# Opcional: descomenta y pon una clave segura generada con secrets.token_hex(32)
# os.environ['DJANGO_SECRET_KEY'] = 'reemplaza-con-una-clave-secreta-larga'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
