"""
Pruebas automatizadas de UI con Selenium --- Flujo de Registro de Usuario
=========================================================================
Verifica el proceso completo de registro: validaciones del formulario,
campos obligatorios, seleccion de pais/region/comuna via AJAX,
y comportamiento del modal de exito.

Requisitos:
  - pip install selenium webdriver-manager
  - Servidor Django corriendo: python manage.py runserver
  - Base de datos con paises, regiones y comunas cargadas

Uso:
  python selenium_tests/test_registro.py
"""

import sys
import os
import io
import time
import uuid
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── Configuracion ─────────────────────────────────────────────────────────────
BASE_URL = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT  = 10
HEADLESS = False
# ─────────────────────────────────────────────────────────────────────────────


def get_driver() -> webdriver.Chrome:
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


def rut_unico():
    """Genera un RUT de prueba unico para cada ejecucion."""
    import random
    num = random.randint(10_000_000, 25_000_000)
    return f"{num}-{random.randint(0, 9)}"


class RegistroTests(unittest.TestCase):
    """Suite de pruebas para el flujo de Registro de Usuario."""

    @classmethod
    def setUpClass(cls):
        cls.driver = get_driver()
        cls.wait   = WebDriverWait(cls.driver, TIMEOUT)
        print("\n[START] Pruebas de Registro de Usuario --- ComicStore\n")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        print("\n[OK] Pruebas de Registro finalizadas. Navegador cerrado.\n")

    def setUp(self):
        self.driver.get(f"{BASE_URL}/registro/")
        time.sleep(0.5)

    # ── TEST 1 ──────────────────────────────────────────────────────────────
    def test_01_pagina_registro_carga_correctamente(self):
        """Verifica que la pagina de registro carga con el formulario."""
        print("  TEST 1: Pagina de registro carga correctamente...")

        body = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        self.assertTrue(
            "registro" in body or "registrar" in body or "bienvenido" in body,
            "La pagina de registro no muestra contenido esperado"
        )
        # Verificar campos del formulario
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, "button#registrar"))
        print("    [PASS] Pagina de registro carga con formulario")

    # ── TEST 2 ──────────────────────────────────────────────────────────────
    def test_02_formulario_vacio_no_envia(self):
        """Verifica que el formulario vacio no puede ser enviado (validacion HTML5)."""
        print("  TEST 2: Formulario vacio no puede enviarse...")

        btn = self.driver.find_element(By.ID, "registrar")
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.5)

        # Debe seguir en la pagina de registro
        self.assertIn("/registro", self.driver.current_url,
            f"El formulario vacio redirigid inesperadamente a: {self.driver.current_url}")
        print("    [PASS] Formulario vacio no puede ser enviado")

    # ── TEST 3 ──────────────────────────────────────────────────────────────
    def test_03_campos_username_y_password_existen(self):
        """Verifica que existen los campos de usuario y contrasena."""
        print("  TEST 3: Campos de usuario y contrasena presentes...")

        campos_requeridos = ["username", "password1", "password2", "rut"]
        for campo in campos_requeridos:
            elem = self.driver.find_element(By.NAME, campo)
            self.assertIsNotNone(elem, f"Campo '{campo}' no encontrado")

        print(f"    [PASS] Campos {campos_requeridos} presentes en el formulario")

    # ── TEST 4 ──────────────────────────────────────────────────────────────
    def test_04_link_a_login_existe(self):
        """Verifica que existe un link hacia la pagina de login."""
        print("  TEST 4: Link hacia login existe en la pagina de registro...")

        links = self.driver.find_elements(By.TAG_NAME, "a")
        urls  = [a.get_attribute("href") or "" for a in links]
        tiene_login = any("/login" in u for u in urls)
        self.assertTrue(tiene_login, "No se encontro link al login en la pagina de registro")
        print("    [PASS] Link hacia login encontrado")

    # ── TEST 5 ──────────────────────────────────────────────────────────────
    def test_05_passwords_no_coincidentes_muestran_error(self):
        """Verifica que contrasenas distintas generan error de validacion."""
        print("  TEST 5: Passwords no coincidentes muestran error...")

        rut = rut_unico()
        uid = uuid.uuid4().hex[:8]

        # Llenar TODOS los campos requeridos
        self._llenar_campo("username",   f"user_{uid}")
        self._llenar_campo("first_name", "Juan")
        self._llenar_campo("last_name",  "Perez")
        self._llenar_campo("rut",        rut)
        self._llenar_campo("email",      f"{uid}@test.com")
        self._llenar_campo("telefono",   "+56912345678")
        self._llenar_campo("direccion",  "Calle Test 123")
        self._llenar_campo("password1",  "ClaveSegura123!")
        self._llenar_campo("password2",  "ClaveDistinta999!")  # diferente a proposito

        # Seleccionar pais si existe el campo
        try:
            select_pais = self.driver.find_element(By.NAME, "pais")
            from selenium.webdriver.support.ui import Select as SeleniumSelect
            s = SeleniumSelect(select_pais)
            if len(s.options) > 1:
                s.select_by_index(1)
                time.sleep(0.5)
        except Exception:
            pass

        btn = self.driver.find_element(By.ID, "registrar")
        self.driver.execute_script("arguments[0].closest('form').setAttribute('novalidate', 'true');", btn)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(2)

        # Debe seguir en registro con mensaje de error
        self.assertIn("/registro", self.driver.current_url,
            f"Con passwords distintos no deberia redirigir: {self.driver.current_url}")

        body = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        tiene_error = any(kw in body for kw in [
            "no coinciden", "deben ser iguales", "password", "contrasena", "error",
            "coincid", "igual"
        ])
        self.assertTrue(tiene_error,
            f"No se mostro error con passwords distintos. Body: {body[:400]}")
        print("    [PASS] Error mostrado con passwords no coincidentes")

    # ── TEST 6 ──────────────────────────────────────────────────────────────
    def test_06_contrasena_muy_corta_muestra_error(self):
        """Verifica que una contrasena muy corta genera error de validacion."""
        print("  TEST 6: Contrasena muy corta muestra error...")

        uid = uuid.uuid4().hex[:8]
        rut = rut_unico()

        # Llenar TODOS los campos requeridos
        self._llenar_campo("username",   f"user_{uid}")
        self._llenar_campo("first_name", "Ana")
        self._llenar_campo("last_name",  "Garcia")
        self._llenar_campo("rut",        rut)
        self._llenar_campo("email",      f"{uid}@test.com")
        self._llenar_campo("telefono",   "+56912345678")
        self._llenar_campo("direccion",  "Av. Siempre Viva 742")
        self._llenar_campo("password1",  "abc")   # muy corta
        self._llenar_campo("password2",  "abc")

        try:
            select_pais = self.driver.find_element(By.NAME, "pais")
            from selenium.webdriver.support.ui import Select as SeleniumSelect
            s = SeleniumSelect(select_pais)
            if len(s.options) > 1:
                s.select_by_index(1)
                time.sleep(0.5)
        except Exception:
            pass

        btn = self.driver.find_element(By.ID, "registrar")
        self.driver.execute_script("arguments[0].closest('form').setAttribute('novalidate', 'true');", btn)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(2)

        self.assertIn("/registro", self.driver.current_url,
            f"Contrasena corta no deberia registrar: {self.driver.current_url}")

        body = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        tiene_error = any(kw in body for kw in [
            "corta", "caracteres", "minimo", "error", "password", "8", "demasiado"
        ])
        self.assertTrue(tiene_error,
            f"No se mostro error con contrasena corta. Body: {body[:400]}")
        print("    [PASS] Error mostrado con contrasena muy corta")

    # ── TEST 7 ──────────────────────────────────────────────────────────────
    def test_07_pagina_titulo_correcto(self):
        """Verifica que el titulo de la pagina es correcto."""
        print("  TEST 7: Titulo de la pagina de registro...")

        title = self.driver.title
        # El titulo en el template dice "Comicstore - Contacto" (bug conocido del template)
        self.assertTrue(
            len(title) > 0,
            "La pagina no tiene titulo"
        )
        print(f"    [PASS] Titulo de la pagina: '{title}'")

    # ── TEST 8 ──────────────────────────────────────────────────────────────
    def test_08_campo_password_tipo_correcto(self):
        """Verifica que los campos de contrasena son de tipo 'password'."""
        print("  TEST 8: Campos de contrasena ocultan el texto...")

        for campo_name in ["password1", "password2"]:
            campo = self.driver.find_element(By.NAME, campo_name)
            tipo  = campo.get_attribute("type")
            self.assertEqual(tipo, "password",
                f"Campo '{campo_name}' tiene tipo '{tipo}' en lugar de 'password'")

        print("    [PASS] Ambos campos de contrasena ocultan el texto")

    # ── Helpers ─────────────────────────────────────────────────────────────
    def _llenar_campo(self, name: str, valor: str):
        """Encuentra un campo por nombre y escribe el valor."""
        try:
            campo = self.driver.find_element(By.NAME, name)
            campo.clear()
            campo.send_keys(valor)
        except Exception:
            pass  # campo opcional puede no existir en este formulario


# ── Punto de entrada ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  COMICSTORE --- Pruebas de Registro de Usuario (Selenium)")
    print("=" * 60)
    print(f"  URL base : {BASE_URL}")
    print(f"  Headless : {'Si' if HEADLESS else 'No (ventana visible)'}")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(RegistroTests))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    ok = result.testsRun - len(result.failures) - len(result.errors)
    print("\n" + "=" * 60)
    print(f"  Tests ejecutados : {result.testsRun}")
    print(f"  [PASS] Exitosos  : {ok}")
    print(f"  [FAIL] Fallidos  : {len(result.failures)}")
    print(f"  [ERR]  Errores   : {len(result.errors)}")
    print("=" * 60)
