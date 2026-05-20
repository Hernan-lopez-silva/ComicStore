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
from datetime import datetime


# ============================================================================
# FIXTURES DE CONFIGURACIÓN DEL NAVEGADOR
# ============================================================================

@pytest.fixture(scope="session")
def browser_session():
    """Crea una sesión del navegador para la suite completa."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Descomenta para ejecución sin interfaz
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(10)
    yield driver
    driver.quit()


@pytest.fixture
def driver(browser_session):
    """Proporciona una instancia del navegador limpia para cada test."""
    browser_session.delete_all_cookies()
    browser_session.execute_script("window.localStorage.clear();")
    yield browser_session
    # Limpiar después de cada test
    browser_session.delete_all_cookies()


# ============================================================================
# FIXTURES DE DATOS DE PRUEBA - USUARIO
# ============================================================================

@pytest.fixture
def valid_user_data():
    """Datos válidos de un usuario para registro."""
    return {
        'nombre': 'Juan Pérez',
        'email': f'juan.perez.{datetime.now().timestamp()}@example.com',
        'rut': '10000000-2',
        'contraseña': 'Segura123!',
        'confirmar_contraseña': 'Segura123!'
    }


@pytest.fixture
def existing_user_credentials():
    """Credenciales de un usuario existente para login."""
    return {
        'email': 'usuario.existente@comicstore.cl',
        'contraseña': 'SeguraPass123!'
    }


@pytest.fixture
def invalid_email_data():
    """Datos con emails inválidos."""
    return [
        {'email': '', 'descripcion': 'Email vacío'},
        {'email': 'invalid-email', 'descripcion': 'Sin símbolo @'},
        {'email': '@example.com', 'descripcion': 'Sin parte local'},
        {'email': 'usuario@', 'descripcion': 'Sin dominio'},
    ]


@pytest.fixture
def invalid_password_data():
    """Datos con contraseñas inválidas."""
    return [
        {'password': 'short', 'descripcion': 'Muy corta'},
        {'password': 'nouppercase1!', 'descripcion': 'Sin mayúsculas'},
        {'password': 'NOLOWERCASE1!', 'descripcion': 'Sin minúsculas'},
        {'password': 'NoSpecial123', 'descripcion': 'Sin caracteres especiales'},
    ]


# ============================================================================
# FIXTURES DE DATOS DE PRUEBA - PRODUCTOS
# ============================================================================

@pytest.fixture
def search_keywords():
    """Palabras clave para búsqueda de productos."""
    return {
        'valida': 'Spider-Man',
        'no_existente': 'ProductoQueNoExiste123XYZ',
        'caracteres_especiales': '!@#$%^&*()',
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
        'imagen_url': '/images/spider-man-1.jpg'
    }


# ============================================================================
# FIXTURES DE DATOS DE PRUEBA - CARRITO Y COMPRA
# ============================================================================

@pytest.fixture
def cart_product_quantities():
    """Cantidades válidas de productos para agregar al carrito."""
    return [1, 2, 5, 10, 50]


@pytest.fixture
def invalid_cart_quantities():
    """Cantidades inválidas para agregar al carrito."""
    return [0, -1, -10, 101, 1000]


@pytest.fixture
def shipping_address():
    """Dirección de envío válida."""
    return {
        'nombre': 'Juan Pérez',
        'direccion': 'Calle Principal 123',
        'apartamento': 'Apt 4',
        'ciudad': 'Santiago',
        'region': 'Metropolitana',
        'codigo_postal': '8320000',
        'telefono': '+56912345678'
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
        'valido': 'COMICSTORE20',
        'descuento_valido': 20,
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
    return "http://localhost:8000"  # Ajusta según tu ambiente


# ============================================================================
# FIXTURES DE LIMPIEZA Y RESET
# ============================================================================

@pytest.fixture(autouse=True)
def reset_app_state(driver, app_url):
    """Reset automático del estado de la aplicación antes de cada test."""
    # Navegar a home para limpiar sesión
    try:
        driver.get(f"{app_url}/")
    except Exception:
        pass
    yield
    # Limpiar cookies y storage después de cada test
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")


# ============================================================================
# FIXTURES PARA CAPTURA DE PANTALLA Y LOGS
# ============================================================================

import os

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
