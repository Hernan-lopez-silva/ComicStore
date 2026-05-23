"""
Configuración global de pytest para los tests de Selenium de ComicStore.
Define fixtures compartidas, configuración de navegador y datos de prueba.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
from datetime import datetime


# ============================================================================
# FIXTURES DE CONFIGURACIÓN DEL NAVEGADOR
# ============================================================================

@pytest.fixture(scope="session")
def browser_session():
    """Crea una sesión del navegador para la suite completa."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Descomenta para ejecución sin interfaz
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)

    # Navegar a la app antes de cualquier test para que localStorage sea accesible
    driver.get("http://127.0.0.1:8000/")
    yield driver
    driver.quit()


@pytest.fixture
def driver(browser_session, app_url):
    """Proporciona una instancia del navegador limpia para cada test."""
    browser_session.delete_all_cookies()

    # Solo limpiar localStorage si estamos en una página real (no about:blank o data:)
    current_url = browser_session.current_url
    if current_url.startswith("http"):
        try:
            browser_session.execute_script("window.localStorage.clear();")
        except Exception:
            pass

    yield browser_session

    # Limpiar después de cada test
    browser_session.delete_all_cookies()


# ============================================================================
# FIXTURES DE DATOS DE PRUEBA - USUARIO
# ============================================================================

@pytest.fixture
def valid_user_data():
    """Datos válidos de un usuario para registro."""
    ts = int(datetime.now().timestamp())
    return {
        'username': f'testuser{ts}',
        'nombre': 'Juan',
        'apellido': 'Pérez',
        'email': f'juan.perez.{ts}@example.com',
        'rut': '10000000-2',
        'telefono': '+56912345678',
        'direccion': 'Calle Principal 123',
        'password1': 'Segura123!',
        'password2': 'Segura123!',
    }


@pytest.fixture
def existing_user_credentials():
    """Credenciales de un usuario existente para login.
    
    IMPORTANTE: Este usuario debe existir en la base de datos.
    Crearlo con: python manage.py shell -c "
        from django.contrib.auth.models import User
        User.objects.create_user('testselenium', password='TestPass123!')
    "
    """
    return {
        'username': 'testselenium',
        'password': 'TestPass123!'
    }


# ============================================================================
# FIXTURES DE DATOS DE PRUEBA - PRODUCTOS
# ============================================================================

@pytest.fixture
def search_keywords():
    """Palabras clave para búsqueda de productos."""
    return {
        'valida': 'Spider',
        'no_existente': 'ProductoQueNoExiste123XYZ',
        'caracteres_especiales': '!@#',
        'muy_corta': 'X',
    }


@pytest.fixture
def product_filter_data():
    """Datos para filtrado de productos."""
    return {
        'categoria': 'Comics Nacionales',
        'precio_minimo': 5000,
        'precio_maximo': 50000,
        'ordenar_por': 'precio_ascendente',
    }


@pytest.fixture
def comic_product():
    """Datos de un producto cómic válido."""
    return {
        'titulo': 'Amazing Spider-Man #1',
        'autor': 'Stan Lee',
        'editorial': 'Marvel Comics',
        'precio': 15000,
        'stock': 50,
        'descripcion': 'Primera aparición de Spider-Man',
        'categoria': 'Comics Internacionales',
    }


# ============================================================================
# FIXTURES DE DATOS DE PRUEBA - CARRITO Y COMPRA
# ============================================================================

@pytest.fixture
def cart_product_quantities():
    """Cantidades válidas de productos para agregar al carrito."""
    return [1, 2, 5]


@pytest.fixture
def invalid_cart_quantities():
    """Cantidades inválidas para agregar al carrito."""
    return [0, -1, -10]


@pytest.fixture
def shipping_address():
    """Dirección de envío válida."""
    return {
        'name': 'Juan Pérez',
        'email': 'juan@example.com',
        'phone': '+56912345678',
        'address': 'Calle Principal 123',
        'city': 'Santiago',
        'region': 'Región Metropolitana',
        'postal_code': '8320000',
    }


@pytest.fixture
def payment_data():
    """Datos de pago válidos."""
    return {
        'numero_tarjeta': '4111111111111111',
        'nombre_titular': 'Juan Pérez',
        'mes_vencimiento': '12',
        'ano_vencimiento': '2025',
        'cvv': '123'
    }


@pytest.fixture
def coupon_data():
    """Datos de cupones de descuento."""
    return {
        'valido': 'COMICSTORE1',
        'descuento_valido': 10,
        'expirado': 'OLDCOUPON',
        'no_existente': 'INVALIDCODE123',
    }


# ============================================================================
# FIXTURES DE UTILIDAD Y ESPERA
# ============================================================================

@pytest.fixture
def wait(driver):
    """WebDriverWait configurado para esperar elementos."""
    return WebDriverWait(driver, 10)


@pytest.fixture
def wait_short(driver):
    """WebDriverWait con espera más corta."""
    return WebDriverWait(driver, 5)


@pytest.fixture
def app_url():
    """URL base de la aplicación."""
    return "http://127.0.0.1:8000"


# ============================================================================
# FIXTURES DE LIMPIEZA Y RESET
# ============================================================================

@pytest.fixture(autouse=True)
def reset_app_state(driver, app_url):
    """Reset automático del estado de la aplicación antes de cada test."""
    try:
        driver.get(f"{app_url}/")
    except Exception:
        pass
    yield
    # Limpiar cookies después de cada test
    driver.delete_all_cookies()
    # Limpiar localStorage solo si la URL actual es una página web
    if driver.current_url.startswith("http"):
        try:
            driver.execute_script("window.localStorage.clear();")
        except Exception:
            pass


# ============================================================================
# FIXTURES PARA CAPTURA DE PANTALLA Y LOGS
# ============================================================================

@pytest.fixture
def capture_screenshot(driver, request):
    """Captura screenshot en puntos clave del test."""
    os.makedirs("screenshots", exist_ok=True)

    def _capture(description=""):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_name = request.node.name
        if description:
            filename = f"screenshots/{test_name}_{description}_{timestamp}.png"
        else:
            filename = f"screenshots/{test_name}_{timestamp}.png"

        driver.save_screenshot(filename)
        return filename

    return _capture


@pytest.fixture(autouse=True)
def screenshot_on_failure(request, driver):
    """Captura automáticamente si el test falla."""
    yield

    # Solo capturar si el test falló
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        os.makedirs("screenshots", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/FAILURE_{request.node.name}_{timestamp}.png"
        try:
            driver.save_screenshot(filename)
        except Exception:
            pass


@pytest.fixture
def log_browser_errors(driver):
    """Registra errores del navegador."""
    def _get_errors():
        logs = driver.get_log('browser')
        errors = [log for log in logs if log['level'] == 'SEVERE']
        return errors
    return _get_errors
