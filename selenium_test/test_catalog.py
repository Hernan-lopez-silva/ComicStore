"""
Tests del Catálogo de Productos de ComicStore.
Cubre RF-06 (Detalle), RF-07 (Crear), RF-08 (Actualizar), RF-09 (Eliminar), RF-10 (Búsqueda).

URLs reales de la aplicación:
  - Landing/catálogo:  /
  - Detalle producto:  /producto/?id=<id>
  - CRUD listar:       /crud/listar/   (requiere superusuario)
  - CRUD crear:        /crud/crear/    (requiere superusuario)
  - CRUD editar:       /crud/editar/<id>/
  - CRUD eliminar:     /crud/eliminar/<id>/  (redirect directo con confirm())

Selectores reales:
  - Tarjetas de producto en landing:  #comics .card
  - Botón comprar:                    #comics .card .btn
  - Campo búsqueda:                   input[name='q']
  - Detalle: #titleComic, #priceComic, #imgComic, .comic-description
  - CRUD crear/editar: id_title, id_description, id_img_path, id_price
  - CRUD guardar:      button[type='submit']
  - CRUD filas:        table tbody tr
  - CRUD eliminar:     a[href*='eliminar']  (confirm() nativo del navegador)
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


# ---------------------------------------------------------------------------
# Helper: login como superusuario para tests de administración
# ---------------------------------------------------------------------------
def _admin_login(driver, wait, app_url, credentials):
    driver.get(f"{app_url}/login/")
    wait.until(EC.presence_of_element_located((By.ID, "id_username"))).send_keys(
        credentials['username']
    )
    driver.find_element(By.ID, "id_password").send_keys(credentials['password'])
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    wait.until(EC.presence_of_element_located((By.ID, "dropdownMenuButton")))


class TestProductDetail:
    """CP-RF-06: Ver detalle de producto"""

    def test_rf_06_01_view_product_detail_with_valid_id(self, driver, app_url, wait, capture_screenshot):
        """
        CP-RF-06-01: Verificar que se puede visualizar detalle de un producto válido.

        Pasos:
        1. Navegar al landing (/) donde se listan los productos
        2. Hacer clic en el botón "Comprar" del primer producto
        3. Verificar que la página de detalle muestra la información

        Nota: requiere que exista al menos un producto en la base de datos.
        """
        driver.get(f"{app_url}/")
        capture_screenshot("paso1_landing")

        # Esperar que cargue la galería de productos
        productos_btn = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#comics .card .btn"))
        )
        assert len(productos_btn) > 0

        # Hacer clic en el botón "Comprar" del primer producto
        productos_btn[0].click()
        capture_screenshot("paso2_detalle_producto")

        # Verificar elementos de detalle en /producto/?id=N
        wait.until(EC.presence_of_element_located((By.ID, "titleComic")))
        assert driver.find_element(By.ID, "titleComic")
        assert driver.find_element(By.ID, "priceComic")

    def test_rf_06_02_product_detail_shows_all_information(self, driver, app_url, wait):
        """
        CP-RF-06-02: Verificar que el detalle muestra la información del producto.
        """
        driver.get(f"{app_url}/")

        productos_btn = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#comics .card .btn"))
        )
        productos_btn[0].click()

        wait.until(EC.presence_of_element_located((By.ID, "titleComic")))

        assert driver.find_element(By.ID, "imgComic")
        assert driver.find_element(By.ID, "titleComic")
        assert driver.find_element(By.ID, "priceComic")

    def test_rf_06_03_product_detail_invalid_id_shows_error(self, driver, app_url, wait):
        """
        CP-RF-06-03: Verificar que un ID inválido muestra la página 404.
        """
        driver.get(f"{app_url}/producto/?id=99999999")

        # Django devuelve 404 cuando el producto no existe
        assert "404" in driver.page_source or "no encontrado" in driver.page_source.lower() \
               or driver.title == "404"


class TestCreateProduct:
    """CP-RF-07: Crear nuevo producto (requiere superusuario)"""

    def test_rf_07_01_admin_can_create_product_with_valid_data(self, driver, app_url, comic_product, wait, admin_credentials):
        """
        CP-RF-07-01: Verificar que el admin puede crear un producto con datos válidos.

        Precondición: debe existir un superusuario con las credenciales de admin_credentials.
        """
        _admin_login(driver, wait, app_url, admin_credentials)
        driver.get(f"{app_url}/crud/crear/")

        wait.until(EC.presence_of_element_located((By.ID, "id_title"))).send_keys(comic_product['title'])
        driver.find_element(By.ID, "id_description").send_keys(comic_product['description'])
        driver.find_element(By.ID, "id_img_path").send_keys(comic_product['img_path'])
        driver.find_element(By.ID, "id_price").send_keys(comic_product['price'])

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Tras crear exitosamente, redirige al listado
        wait.until(EC.url_contains("listar"))
        assert "crear" not in driver.current_url.lower()

    @pytest.mark.parametrize("campo_faltante", ["id_title", "id_price"])
    def test_rf_07_02_creation_fails_with_missing_required_fields(self, driver, app_url, comic_product, wait, admin_credentials, campo_faltante):
        """
        CP-RF-07-02: Verificar que la creación falla si faltan campos requeridos.
        Los campos requeridos en FormComic son: title y price.
        """
        _admin_login(driver, wait, app_url, admin_credentials)
        driver.get(f"{app_url}/crud/crear/")

        wait.until(EC.presence_of_element_located((By.ID, "id_title")))

        if campo_faltante != "id_title":
            driver.find_element(By.ID, "id_title").send_keys(comic_product['title'])
        if campo_faltante != "id_price":
            driver.find_element(By.ID, "id_price").send_keys(comic_product['price'])

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Con campo requerido faltante, Django devuelve el formulario con errorlist
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".errorlist")))
        assert "crear" in driver.current_url.lower()

    def test_rf_07_03_creation_fails_with_invalid_price(self, driver, app_url, comic_product, wait, admin_credentials):
        """
        CP-RF-07-03: Verificar que un precio inválido (texto) impide la creación.
        """
        _admin_login(driver, wait, app_url, admin_credentials)
        driver.get(f"{app_url}/crud/crear/")

        wait.until(EC.presence_of_element_located((By.ID, "id_title"))).send_keys(comic_product['title'])
        driver.find_element(By.ID, "id_price").send_keys("precio_invalido")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".errorlist")))


class TestUpdateProduct:
    """CP-RF-08: Actualizar producto (requiere superusuario)"""

    def test_rf_08_01_admin_can_update_product_with_valid_data(self, driver, app_url, wait, admin_credentials):
        """
        CP-RF-08-01: Verificar que el admin puede actualizar un producto.
        Precondición: debe existir un producto con id=1.
        """
        _admin_login(driver, wait, app_url, admin_credentials)
        driver.get(f"{app_url}/crud/editar/1/")

        wait.until(EC.presence_of_element_located((By.ID, "id_title")))

        titulo_field = driver.find_element(By.ID, "id_title")
        titulo_field.clear()
        titulo_field.send_keys("Título Actualizado - Test")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Redirige al listado tras guardar
        wait.until(EC.url_contains("listar"))
        assert "editar" not in driver.current_url.lower()

    def test_rf_08_02_update_preserves_other_product_fields(self, driver, app_url, wait, admin_credentials):
        """
        CP-RF-08-02: Verificar que actualizar el título no cambia el precio.
        """
        _admin_login(driver, wait, app_url, admin_credentials)
        driver.get(f"{app_url}/crud/editar/1/")

        wait.until(EC.presence_of_element_located((By.ID, "id_price")))
        precio_original = driver.find_element(By.ID, "id_price").get_attribute("value")

        titulo_field = driver.find_element(By.ID, "id_title")
        titulo_field.clear()
        titulo_field.send_keys("Nuevo Título Test")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Volver a editar y verificar que el precio se conservó
        driver.get(f"{app_url}/crud/editar/1/")
        wait.until(EC.presence_of_element_located((By.ID, "id_price")))
        assert driver.find_element(By.ID, "id_price").get_attribute("value") == precio_original

    def test_rf_08_03_update_fails_with_invalid_price_value(self, driver, app_url, wait, admin_credentials):
        """
        CP-RF-08-03: Verificar que un precio inválido impide la actualización.
        """
        _admin_login(driver, wait, app_url, admin_credentials)
        driver.get(f"{app_url}/crud/editar/1/")

        wait.until(EC.presence_of_element_located((By.ID, "id_price")))
        precio_field = driver.find_element(By.ID, "id_price")
        precio_field.clear()
        precio_field.send_keys("precio_invalido")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".errorlist")))


class TestDeleteProduct:
    """CP-RF-09: Eliminar producto (requiere superusuario)

    La eliminación usa un confirm() nativo del navegador (no un modal HTML).
    Selenium gestiona el diálogo con driver.switch_to.alert.
    """

    def test_rf_09_01_admin_can_delete_product(self, driver, app_url, wait, admin_credentials):
        """
        CP-RF-09-01: Verificar que el admin puede eliminar un producto.
        Precondición: debe existir al menos un producto en la base de datos.
        """
        _admin_login(driver, wait, app_url, admin_credentials)
        driver.get(f"{app_url}/crud/listar/")

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table a[href*='eliminar']")))
        filas_inicial = len(driver.find_elements(By.CSS_SELECTOR, "table tbody tr"))

        # El enlace tiene onclick="return confirm('...')" → activa diálogo nativo
        driver.find_element(By.CSS_SELECTOR, "table a[href*='eliminar']").click()
        driver.switch_to.alert.accept()

        # Tras eliminar, redirige al listado con una fila menos
        wait.until(EC.url_contains("listar"))
        filas_final = len(driver.find_elements(By.CSS_SELECTOR, "table tbody tr"))
        assert filas_final == filas_inicial - 1

    def test_rf_09_02_delete_requires_confirmation(self, driver, app_url, wait, admin_credentials):
        """
        CP-RF-09-02: Verificar que la eliminación activa un diálogo de confirmación.
        """
        _admin_login(driver, wait, app_url, admin_credentials)
        driver.get(f"{app_url}/crud/listar/")

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table a[href*='eliminar']")))
        driver.find_element(By.CSS_SELECTOR, "table a[href*='eliminar']").click()

        # Verificar que el diálogo nativo está presente
        alert = driver.switch_to.alert
        assert alert.text  # el diálogo tiene texto
        alert.accept()

    def test_rf_09_03_cancel_delete_preserves_product(self, driver, app_url, wait, admin_credentials):
        """
        CP-RF-09-03: Verificar que cancelar el confirm() no elimina el producto.
        """
        _admin_login(driver, wait, app_url, admin_credentials)
        driver.get(f"{app_url}/crud/listar/")

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table a[href*='eliminar']")))
        filas_inicial = len(driver.find_elements(By.CSS_SELECTOR, "table tbody tr"))

        driver.find_element(By.CSS_SELECTOR, "table a[href*='eliminar']").click()
        driver.switch_to.alert.dismiss()  # Cancelar el confirm()

        # El producto sigue en la tabla
        filas_actual = len(driver.find_elements(By.CSS_SELECTOR, "table tbody tr"))
        assert filas_actual == filas_inicial


class TestProductSearch:
    """CP-RF-10: Búsqueda de productos en el landing (/)"""

    @pytest.mark.parametrize("keyword,expected_min", [
        ("Spider-Man", 1),
        ("Batman", 1),
        ("Marvel", 1),
    ])
    def test_rf_10_01_search_returns_relevant_results(self, driver, app_url, wait, keyword, expected_min):
        """
        CP-RF-10-01: Verificar que la búsqueda retorna resultados relevantes.
        El formulario de búsqueda está en la navbar (base.html), usa GET ?q=.
        Precondición: los productos buscados deben existir en la base de datos.
        """
        driver.get(f"{app_url}/")

        search_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='q']"))
        )
        search_field.clear()
        search_field.send_keys(keyword)
        search_field.send_keys(Keys.RETURN)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#comics .card")))
        productos = driver.find_elements(By.CSS_SELECTOR, "#comics .card")

        assert len(productos) >= expected_min

    def test_rf_10_02_search_no_results_shows_message(self, driver, app_url, search_keywords, wait):
        """
        CP-RF-10-02: Verificar que una búsqueda sin resultados no muestra tarjetas.
        """
        driver.get(f"{app_url}/")

        search_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='q']"))
        )
        search_field.clear()
        search_field.send_keys(search_keywords['no_existente'])
        search_field.send_keys(Keys.RETURN)

        # El template solo muestra .card si hay resultados; sin ellos la galería está vacía
        import time
        time.sleep(1)
        productos = driver.find_elements(By.CSS_SELECTOR, "#comics .card")
        assert len(productos) == 0 or \
               "no se encontraron" in driver.page_source.lower() or \
               "recién llegados" not in driver.page_source.lower()

    def test_rf_10_03_search_is_case_insensitive(self, driver, app_url, wait):
        """
        CP-RF-10-03: Verificar que la búsqueda no distingue mayúsculas/minúsculas.
        Precondición: existen productos con "spider-man" en el título.
        """
        driver.get(f"{app_url}/")

        search_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='q']"))
        )
        search_field.send_keys("spider-man")
        search_field.send_keys(Keys.RETURN)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#comics")))
        resultados_min = len(driver.find_elements(By.CSS_SELECTOR, "#comics .card"))

        driver.get(f"{app_url}/")
        search_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='q']"))
        )
        search_field.send_keys("SPIDER-MAN")
        search_field.send_keys(Keys.RETURN)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#comics")))
        resultados_may = len(driver.find_elements(By.CSS_SELECTOR, "#comics .card"))

        assert resultados_min == resultados_may
