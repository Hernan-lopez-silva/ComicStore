"""
Suite de Tests Selenium para ComicStore.

Módulo de pruebas automatizadas que valida la funcionalidad de la aplicación
web ComicStore según los Requerimientos Funcionales especificados.

Estructura:
- conftest.py: Configuración global, fixtures de navegador y datos
- test_authentication.py: Tests de autenticación y sesión (RF-01, RF-02, RF-05)
- test_catalog.py: Tests de catálogo y búsqueda (RF-06, RF-07, RF-08, RF-09, RF-10)
- test_cart_and_checkout.py: Tests de carrito y compra (RF-03, RF-04, RF-11, RF-12, RF-13)

Uso:
    pytest                    # Ejecutar todos los tests
    pytest -m authentication  # Ejecutar por categoría
    pytest -v               # Modo verbose
    pytest --html=report.html # Generar reporte HTML
"""

__version__ = "1.0.0"
__author__ = "Maestro Hernán (her.lopezs@duocuc.cl)"
__created__ = "2026-05-19"
