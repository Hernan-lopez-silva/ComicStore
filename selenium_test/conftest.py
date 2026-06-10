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
    # Navegar a la app antes de limpiar localStorage:
    # en una página data: el acceso a localStorage lanza excepción.
    try:
        browser_session.get("http://127.0.0.1:8000/")
        browser_session.execute_script("window.localStorage.clear();")
    except Exception:
        pass
    yield browser_session
    browser_session.delete_all_cookies()


# ============================================================================
# FIXTURES DE DATOS DE PRUEBA - USUARIO
# ============================================================================

@pytest.fixture
def valid_user_data():
    """Datos válidos de un usuario para registro.
    Parámetros del Word para RF-01-01:
    juan, Juan Pérez, juan@correo.com, 10000000-2, +56950184516,
    Chile, Región Metropolitana, Maipú, Segura123!
    """
    return {
        'username': 'juan',
        'nombre': 'Juan',
        'apellido': 'Pérez',
        'email': 'juan@correo.com',
        'rut': '10000000-2',
        'telefono': '+56950184516',
        'direccion': 'Calle Principal 123',
        'pais': '1',
        'region': '16',
        'comuna': '320',
        'password1': 'Segura123!',
        'password2': 'Segura123!',
    }


@pytest.fixture
def existing_user_credentials():
    """Credenciales de un usuario existente para login.
    El usuario debe existir en la base de datos antes de ejecutar los tests.
    Parámetros del Word - RF-02-01: usuario@correo.com / Segura123!
    Crear con: python manage.py createsuperuser --username usuario --email usuario@correo.com
    """
    return {
        'username': 'usuario',
        'password': 'Segura123!',
    }


@pytest.fixture
def admin_credentials():
    """Credenciales de un superusuario administrador.
    El usuario debe existir en la base de datos con is_superuser=True.
    """
    return {
        'username': 'admin',
        'password': 'Admin123!',
    }


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
    """Datos de un producto cómic válido para el formulario CRUD."""
    return {
        'title': 'Amazing Spider-Man Test',
        'description': 'Primera aparición de Spider-Man - Test',
        'img_path': '/static/img/test.jpg',
        'price': '15000',
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
    """Dirección de envío válida para el formulario de checkout."""
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
        'no_existente': 'INVALIDCODE123',
        'expirado': 'OLDCOUPON',
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
    driver.delete_all_cookies()
    try:
        driver.execute_script("window.localStorage.clear();")
    except Exception:
        pass


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


# ============================================================================
# SETUP AUTOMÁTICO DE BASE DE DATOS PARA TESTS
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Crea automáticamente el usuario 'usuario' para los tests de login/logout.
    Parámetros del Word para RF-02 y RF-05:
    - username: usuario
    - email: usuario@correo.com
    - password: Segura123!

    Requiere que la app Django esté corriendo para acceder a la BD.
    """
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comicstore.settings')
    django.setup()

    from django.contrib.auth.models import User

    username = 'usuario'
    email = 'usuario@correo.com'
    password = 'Segura123!'

    # Crear usuario si no existe
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
    else:
        # Actualizar email si el usuario ya existe
        user = User.objects.get(username=username)
        user.email = email
        user.set_password(password)
        user.save()

    yield

    # Cleanup opcional: descomentar si se quiere eliminar el usuario al finalizar tests
    # User.objects.filter(username=username).delete()
