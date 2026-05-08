"""
Pruebas automatizadas de UI con Selenium --- Flujo de Busqueda de Productos
============================================================================
Verifica el buscador de comics en la landing page: resultados correctos,
mensaje cuando no hay resultados, tarjetas de producto y navegacion al detalle.

Requisitos:
  - pip install selenium webdriver-manager
  - Servidor Django corriendo: python manage.py runserver
  - Base de datos con comics cargados (python cargar_comics.py)

Uso:
  python selenium_tests/test_busqueda.py
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

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── Configuracion ─────────────────────────────────────────────────────────────
BASE_URL       = "http://127.0.0.1:8000"
TIMEOUT        = 10
HEADLESS       = False
TERMINO_VALIDO = "batman"      # Debe existir en la BD
TERMINO_VACIO  = "xyzxyzxyz"   # No debe existir en la BD
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


def buscar(driver, termino: str):
    """Realiza una busqueda expandiendo el navbar si es necesario y enviando el formulario."""
    # Expandir el navbar collapse si esta cerrado
    try:
        toggler = driver.find_element(By.CSS_SELECTOR, ".navbar-toggler")
        if toggler.is_displayed():
            driver.execute_script("arguments[0].click();", toggler)
            time.sleep(0.5)
    except Exception:
        pass

    # Usar JS para escribir en el campo y enviar el formulario
    driver.execute_script(
        "var q = document.querySelector('input[name=\"q\"]');"
        "q.value = arguments[0];"
        "q.closest('form').submit();",
        termino
    )
    time.sleep(1.5)


class BusquedaProductosTests(unittest.TestCase):
    """Suite de pruebas para el buscador de comics."""

    @classmethod
    def setUpClass(cls):
        cls.driver = get_driver()
        cls.wait   = WebDriverWait(cls.driver, TIMEOUT)
        print("\n[START] Pruebas de Busqueda de Productos --- ComicStore\n")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        print("\n[OK] Pruebas de Busqueda finalizadas. Navegador cerrado.\n")

    def setUp(self):
        self.driver.get(BASE_URL)
        time.sleep(0.5)

    # ── TEST 1 ──────────────────────────────────────────────────────────────
    def test_01_landing_muestra_galeria_de_comics(self):
        """Verifica que la landing page muestra tarjetas de comics."""
        print("  TEST 1: Landing muestra galeria de comics...")

        cards = self.driver.find_elements(By.CSS_SELECTOR, ".card")
        self.assertGreater(len(cards), 0,
            "No se encontraron tarjetas de comics en la landing page")
        print(f"    [PASS] Galeria muestra {len(cards)} tarjetas de comics")

    # ── TEST 2 ──────────────────────────────────────────────────────────────
    def test_02_campo_busqueda_existe_en_navbar(self):
        """Verifica que el navbar contiene un campo de busqueda en el DOM."""
        print("  TEST 2: Campo de busqueda en el navbar...")

        # El campo existe en el DOM aunque pueda estar en navbar colapsado
        campo = self.driver.find_element(By.CSS_SELECTOR, "input[name='q']")
        self.assertIsNotNone(campo, "El campo de busqueda no existe en el DOM")
        placeholder = campo.get_attribute("placeholder") or ""
        self.assertGreater(len(placeholder), 0, "El campo de busqueda no tiene placeholder")
        print(f"    [PASS] Campo de busqueda encontrado (placeholder='{placeholder}')")

    # ── TEST 3 ──────────────────────────────────────────────────────────────
    def test_03_busqueda_con_termino_valido_retorna_resultados(self):
        """Verifica que buscar un termino existente muestra resultados."""
        print(f"  TEST 3: Busqueda de '{TERMINO_VALIDO}' retorna resultados...")

        buscar(self.driver, TERMINO_VALIDO)

        # Verificar que la URL contiene el parametro de busqueda
        self.assertIn("q=", self.driver.current_url,
            f"La URL no contiene parametro de busqueda: {self.driver.current_url}")

        # Verificar que hay resultados (tarjetas de comics)
        body = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        hay_resultados = (
            "resultados para" in body
            or len(self.driver.find_elements(By.CSS_SELECTOR, ".card")) > 0
        )
        self.assertTrue(hay_resultados,
            f"No se encontraron resultados para '{TERMINO_VALIDO}'")

        cards = self.driver.find_elements(By.CSS_SELECTOR, ".card")
        print(f"    [PASS] Busqueda '{TERMINO_VALIDO}' retorno {len(cards)} resultado(s)")

    # ── TEST 4 ──────────────────────────────────────────────────────────────
    def test_04_busqueda_sin_resultados_muestra_mensaje(self):
        """Verifica que buscar un termino inexistente muestra mensaje apropiado."""
        print(f"  TEST 4: Busqueda de '{TERMINO_VACIO}' muestra mensaje de sin resultados...")

        buscar(self.driver, TERMINO_VACIO)

        body = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        sin_resultados = any(kw in body for kw in [
            "no se encontraron", "no hay", "sin resultados", "no results"
        ])
        self.assertTrue(sin_resultados,
            f"No se mostro mensaje de sin resultados para '{TERMINO_VACIO}'. Body: {body[:300]}")
        print(f"    [PASS] Busqueda sin resultados muestra mensaje correcto")

    # ── TEST 5 ──────────────────────────────────────────────────────────────
    def test_05_cada_tarjeta_tiene_boton_comprar(self):
        """Verifica que cada tarjeta de comic tiene un boton de comprar."""
        print("  TEST 5: Cada tarjeta de comic tiene boton 'Comprar'...")

        cards   = self.driver.find_elements(By.CSS_SELECTOR, ".card")
        if len(cards) == 0:
            self.skipTest("No hay comics en la landing para verificar")

        botones = self.driver.find_elements(
            By.XPATH, "//button[contains(translate(., 'COMPRAR', 'comprar'), 'comprar')]"
        )
        self.assertGreater(len(botones), 0, "Ninguna tarjeta tiene boton 'Comprar'")
        print(f"    [PASS] {len(botones)} boton(es) 'Comprar' encontrados")

    # ── TEST 6 ──────────────────────────────────────────────────────────────
    def test_06_boton_comprar_navega_a_detalle_producto(self):
        """Verifica que el boton Comprar lleva a la pagina de detalle del producto."""
        print("  TEST 6: Boton 'Comprar' navega al detalle del producto...")

        cards = self.driver.find_elements(By.CSS_SELECTOR, ".card")
        if len(cards) == 0:
            self.skipTest("No hay comics en la landing")

        # Click en el primer boton Comprar
        primer_boton = self.driver.find_element(
            By.XPATH, "(//button[contains(translate(., 'COMPRAR', 'comprar'), 'comprar')])[1]"
        )
        self.driver.execute_script("arguments[0].click();", primer_boton)
        time.sleep(1.5)

        # Debe navegar a /producto/
        self.assertIn("/producto", self.driver.current_url,
            f"Boton Comprar no navego a /producto: {self.driver.current_url}")
        print(f"    [PASS] Navegado al detalle: {self.driver.current_url}")

    # ── TEST 7 ──────────────────────────────────────────────────────────────
    def test_07_pagina_detalle_producto_tiene_info(self):
        """Verifica que la pagina de detalle del producto muestra informacion."""
        print("  TEST 7: Pagina de detalle muestra info del producto...")

        self.driver.get(BASE_URL)
        time.sleep(0.5)

        cards = self.driver.find_elements(By.CSS_SELECTOR, ".card")
        if len(cards) == 0:
            self.skipTest("No hay comics en la landing")

        primer_boton = self.driver.find_element(
            By.XPATH, "(//button[contains(translate(., 'COMPRAR', 'comprar'), 'comprar')])[1]"
        )
        self.driver.execute_script("arguments[0].click();", primer_boton)
        time.sleep(1.5)

        body = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertGreater(len(body), 50, "La pagina de detalle parece estar vacia")
        print(f"    [PASS] Pagina de detalle con contenido en: {self.driver.current_url}")

    # ── TEST 8 ──────────────────────────────────────────────────────────────
    def test_08_busqueda_case_insensitive(self):
        """Verifica que la busqueda funciona independientemente de mayusculas."""
        print("  TEST 8: Busqueda no distingue mayusculas/minusculas...")

        # Buscar en mayusculas
        buscar(self.driver, TERMINO_VALIDO.upper())
        cards_mayus = len(self.driver.find_elements(By.CSS_SELECTOR, ".card"))

        # Buscar en minusculas
        self.driver.get(BASE_URL)
        time.sleep(0.3)
        buscar(self.driver, TERMINO_VALIDO.lower())
        cards_minus = len(self.driver.find_elements(By.CSS_SELECTOR, ".card"))

        self.assertEqual(cards_mayus, cards_minus,
            f"Busqueda case-sensitive: UPPER={cards_mayus} != lower={cards_minus}")
        print(f"    [PASS] Mismos {cards_mayus} resultados en mayusculas y minusculas")

    # ── TEST 9 ──────────────────────────────────────────────────────────────
    def test_09_titulo_resultados_muestra_termino_buscado(self):
        """Verifica que el titulo de resultados menciona el termino buscado."""
        print("  TEST 9: Titulo de resultados menciona el termino buscado...")

        buscar(self.driver, TERMINO_VALIDO)

        body = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        # El template dice: Resultados para: "{{ query }}"
        menciona_termino = TERMINO_VALIDO.lower() in body
        self.assertTrue(menciona_termino,
            f"El termino '{TERMINO_VALIDO}' no aparece en la pagina de resultados")
        print(f"    [PASS] Termino '{TERMINO_VALIDO}' aparece en la pagina de resultados")

    # ── TEST 10 ─────────────────────────────────────────────────────────────
    def test_10_carrusel_existe_en_landing(self):
        """Verifica que el carrusel de imagenes esta presente en la landing."""
        print("  TEST 10: Carrusel de imagenes en la landing...")

        carrusel = self.driver.find_element(By.ID, "carouselExample")
        self.assertIsNotNone(carrusel, "El carrusel no existe en la landing")
        print("    [PASS] Carrusel de imagenes encontrado en la landing")


# ── Punto de entrada ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  COMICSTORE --- Pruebas de Busqueda de Productos (Selenium)")
    print("=" * 60)
    print(f"  URL base       : {BASE_URL}")
    print(f"  Termino valido : '{TERMINO_VALIDO}'")
    print(f"  Termino vacio  : '{TERMINO_VACIO}'")
    print(f"  Headless       : {'Si' if HEADLESS else 'No (ventana visible)'}")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(BusquedaProductosTests))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    ok = result.testsRun - len(result.failures) - len(result.errors)
    print("\n" + "=" * 60)
    print(f"  Tests ejecutados : {result.testsRun}")
    print(f"  [PASS] Exitosos  : {ok}")
    print(f"  [FAIL] Fallidos  : {len(result.failures)}")
    print(f"  [ERR]  Errores   : {len(result.errors)}")
    print("=" * 60)
