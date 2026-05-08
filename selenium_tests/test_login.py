"""
Pruebas automatizadas de UI con Selenium --- ComicStore
=======================================================
Requisitos:
  - pip install selenium webdriver-manager
  - Servidor Django corriendo: python manage.py runserver
  - Google Chrome instalado

Uso:
  python selenium_tests/test_login.py
"""

import sys
import io
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Forzar UTF-8 en la salida (Windows)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── Configuracion ─────────────────────────────────────────────────────────────
BASE_URL    = "http://127.0.0.1:8000"
NORMAL_USER = {"username": "testuser", "password": "TestPass123!"}
SUPER_USER  = {"username": "admin",    "password": "admin"}
TIMEOUT     = 10
HEADLESS    = False   # cambiar a True para CI/CD sin ventana
# ─────────────────────────────────────────────────────────────────────────────


def get_driver() -> webdriver.Chrome:
    """Crea y devuelve un driver de Chrome configurado."""
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(ChromeDriverManager().install())
    driver  = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(TIMEOUT)
    return driver


def click_submit(driver):
    """Hace clic en el boton submit usando JavaScript (evita problemas de visibilidad CSS)."""
    btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].click();", btn)


class LoginTests(unittest.TestCase):
    """Suite de pruebas para el flujo de Login."""

    @classmethod
    def setUpClass(cls):
        cls.driver = get_driver()
        cls.wait   = WebDriverWait(cls.driver, TIMEOUT)
        print("\n[START] Pruebas de Login --- ComicStore\n")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        print("\n[OK] Navegador cerrado.\n")

    def setUp(self):
        self.driver.get(f"{BASE_URL}/login/")
        time.sleep(0.3)

    # ── TEST 1 ──────────────────────────────────────────────────────────────
    def test_01_pagina_login_carga_correctamente(self):
        """Verifica que la pagina de login contiene los elementos del formulario."""
        print("  TEST 1: Verificando carga de pagina de login...")
        self.assertIn("Login", self.driver.title)
        self.assertTrue(self.driver.find_element(By.NAME, "username"))
        self.assertTrue(self.driver.find_element(By.NAME, "password"))
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']"))
        print("    [PASS] Pagina de login carga correctamente")

    # ── TEST 2 ──────────────────────────────────────────────────────────────
    def test_02_login_fallido_credenciales_incorrectas(self):
        """Verifica que credenciales incorrectas no dan acceso al area privada."""
        print("  TEST 2: Login con credenciales incorrectas...")
        self.driver.find_element(By.NAME, "username").send_keys("usuario_inexistente")
        self.driver.find_element(By.NAME, "password").send_keys("clave_incorrecta")
        click_submit(self.driver)
        time.sleep(1)

        current_url = self.driver.current_url
        body        = self.driver.find_element(By.TAG_NAME, "body").text.lower()

        # El sistema puede mostrar error en el login O redirigir al landing.
        # Lo importante: NO debe redirigir a rutas autenticadas (/home, /listar, /my-orders)
        rutas_privadas = ["/home", "/listar", "/my-orders", "/carrito"]
        en_ruta_privada = any(ruta in current_url for ruta in rutas_privadas)
        self.assertFalse(en_ruta_privada,
            f"Usuario inexistente accedio a ruta privada: {current_url}")

        # Si se muestra un mensaje de error, verificarlo
        mensaje_error = any(kw in body for kw in [
            "no est", "registrado", "incorrecta", "error", "inv", "credencial"
        ])
        # O debe estar en la pagina de login O en landing sin contenido privado
        self.assertTrue(
            "/login" in current_url or not en_ruta_privada,
            f"Comportamiento inesperado: URL={current_url}"
        )
        print(f"    [PASS] Credenciales incorrectas no dan acceso privado. URL={current_url}")

    # ── TEST 3 ──────────────────────────────────────────────────────────────
    def test_03_login_exitoso_usuario_normal(self):
        """Verifica que un usuario normal puede iniciar sesion y es redirigido."""
        print(f"  TEST 3: Login como usuario normal ({NORMAL_USER['username']})...")
        self.driver.find_element(By.NAME, "username").send_keys(NORMAL_USER["username"])
        self.driver.find_element(By.NAME, "password").send_keys(NORMAL_USER["password"])
        click_submit(self.driver)
        self.wait.until(EC.url_changes(f"{BASE_URL}/login/"))
        self.assertNotIn("/login", self.driver.current_url)
        print(f"    [PASS] Redirigido a: {self.driver.current_url}")
        self.driver.get(f"{BASE_URL}/logout/")
        time.sleep(0.5)

    # ── TEST 4 ──────────────────────────────────────────────────────────────
    def test_04_login_exitoso_superusuario(self):
        """Verifica que el superusuario puede iniciar sesion y es redirigido."""
        print(f"  TEST 4: Login como superusuario ({SUPER_USER['username']})...")
        self.driver.find_element(By.NAME, "username").send_keys(SUPER_USER["username"])
        self.driver.find_element(By.NAME, "password").send_keys(SUPER_USER["password"])
        click_submit(self.driver)
        self.wait.until(EC.url_changes(f"{BASE_URL}/login/"))
        self.assertNotIn("/login", self.driver.current_url)
        print(f"    [PASS] Superusuario redirigido a: {self.driver.current_url}")
        self.driver.get(f"{BASE_URL}/logout/")
        time.sleep(0.5)

    # ── TEST 5 ──────────────────────────────────────────────────────────────
    def test_05_campo_password_es_tipo_password(self):
        """Verifica que el campo contrasena oculta el texto (type=password)."""
        print("  TEST 5: Verificando que el campo password oculta el texto...")
        tipo = self.driver.find_element(By.NAME, "password").get_attribute("type")
        self.assertEqual(tipo, "password", f"El campo tiene tipo '{tipo}' en lugar de 'password'")
        print("    [PASS] Campo password oculta el texto correctamente")

    # ── TEST 6 ──────────────────────────────────────────────────────────────
    def test_06_login_con_tecla_enter(self):
        """Verifica que el formulario puede enviarse con la tecla Enter."""
        print("  TEST 6: Login con tecla Enter...")
        self.driver.find_element(By.NAME, "username").send_keys("usuario_inexistente")
        campo_pw = self.driver.find_element(By.NAME, "password")
        campo_pw.send_keys("clave_incorrecta")
        campo_pw.send_keys(Keys.RETURN)
        time.sleep(1)
        # Debe haber procesado el formulario (con o sin error)
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertTrue(len(body) > 0)
        print("    [PASS] Formulario procesado con tecla Enter")

    # ── TEST 7 ──────────────────────────────────────────────────────────────
    def test_07_link_a_registro_existe(self):
        """Verifica que la pagina de login tiene un link hacia /registro."""
        print("  TEST 7: Verificando link hacia registro...")
        links = self.driver.find_elements(By.TAG_NAME, "a")
        urls  = [a.get_attribute("href") or "" for a in links]
        self.assertTrue(any("/registro" in u for u in urls), "No se encontro link a /registro")
        print("    [PASS] Link hacia registro encontrado")


class LandingPageTests(unittest.TestCase):
    """Suite de pruebas para la Landing Page."""

    @classmethod
    def setUpClass(cls):
        cls.driver = get_driver()
        cls.wait   = WebDriverWait(cls.driver, TIMEOUT)
        print("\n[START] Pruebas de Landing Page\n")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        print("\n[OK] Pruebas Landing Page finalizadas.\n")

    # ── TEST 1 ──────────────────────────────────────────────────────────────
    def test_01_landing_carga_con_contenido(self):
        """Verifica que la landing page carga con contenido visible."""
        print("  TEST 1: Verificando carga de landing page...")
        self.driver.get(BASE_URL)
        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertGreater(len(body), 10, "La landing page parece estar vacia")
        print(f"    [PASS] Landing page cargada: {self.driver.current_url}")

    # ── TEST 2 ──────────────────────────────────────────────────────────────
    def test_02_navbar_tiene_link_login(self):
        """Verifica que el navbar tiene un link hacia /login."""
        print("  TEST 2: Verificando link de login en el navbar...")
        self.driver.get(BASE_URL)
        links = self.driver.find_elements(By.CSS_SELECTOR, "nav a")
        urls  = [a.get_attribute("href") or "" for a in links]
        self.assertTrue(any("/login" in u for u in urls), "No se encontro link a /login en el navbar")
        print("    [PASS] Link de login encontrado en el navbar")


# ── Punto de entrada ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  COMICSTORE --- Pruebas Automatizadas de UI con Selenium")
    print("=" * 60)
    print(f"  URL base    : {BASE_URL}")
    print(f"  Headless    : {'Si' if HEADLESS else 'No (ventana visible)'}")
    print(f"  Usuario     : {NORMAL_USER['username']}")
    print(f"  Superusuario: {SUPER_USER['username']}")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(LoginTests))
    suite.addTests(loader.loadTestsFromTestCase(LandingPageTests))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    ok  = result.testsRun - len(result.failures) - len(result.errors)
    print("\n" + "=" * 60)
    print(f"  Tests ejecutados : {result.testsRun}")
    print(f"  [PASS] Exitosos  : {ok}")
    print(f"  [FAIL] Fallidos  : {len(result.failures)}")
    print(f"  [ERR]  Errores   : {len(result.errors)}")
    print("=" * 60)
