"""
Tests del Catálogo de Productos de ComicStore.
Cubre RF-06 (Detalle), RF-07 (Crear), RF-08 (Actualizar), RF-09 (Eliminar), RF-10 (Búsqueda).
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


class TestProductDetail:
    """CP-RF-06: Ver detalle de producto"""

    def test_rf_06_01_view_product_detail_with_valid_id(self, driver, app_url, wait, capture_screenshot):
        """
        CP-RF-06-01: Verificar que se puede visualizar detalle de un producto válido.

        Pasos:
        1. Navegar al catálogo
        2. Seleccionar un producto
        3. Verificar que se muestra información completa

        Resultado: Detalle del producto visible
        """
        driver.get(f"{app_url}/catalogo")
        capture_screenshot("paso1_catalogo")

        # Esperar que cargue lista de productos
        productos = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "producto-item")))
        assert len(productos) > 0

        # Hacer clic en el primer producto
        productos[0].click()

        # Verificar que se muestran detalles
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "producto-detalle")))
        capture_screenshot("paso2_detalle_producto")

        assert driver.find_element(By.CLASS_NAME, "producto-titulo")
        assert driver.find_element(By.CLASS_NAME, "producto-precio")
        assert driver.find_element(By.CLASS_NAME, "producto-descripcion")

    def test_rf_06_02_product_detail_shows_all_information(self, driver, app_url, wait):
        """
        CP-RF-06-02: Verificar que el detalle muestra toda la información del producto.
        """
        driver.get(f"{app_url}/catalogo")

        productos = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "producto-item")))
        productos[0].click()

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "producto-detalle")))

        # Verificar presencia de todos los campos
        assert driver.find_element(By.CLASS_NAME, "producto-imagen")
        assert driver.find_element(By.CLASS_NAME, "producto-titulo")
        assert driver.find_element(By.CLASS_NAME, "producto-autor")
        assert driver.find_element(By.CLASS_NAME, "producto-editorial")
        assert driver.find_element(By.CLASS_NAME, "producto-precio")
        assert driver.find_element(By.CLASS_NAME, "producto-stock")
        assert driver.find_element(By.CLASS_NAME, "producto-descripcion")

    def test_rf_06_03_product_detail_invalid_id_shows_error(self, driver, app_url, wait):
        """
        CP-RF-06-03: Verificar que ID inválido muestra error.
        """
        driver.get(f"{app_url}/producto/id-invalido-12345")

        # Debe mostrar error o redirigir
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error-404")))
        assert "404" in driver.page_source or "no encontrado" in driver.page_source.lower()


class TestCreateProduct:
    """CP-RF-07: Crear nuevo producto (Admin)"""

    def test_rf_07_01_admin_can_create_product_with_valid_data(self, driver, app_url, comic_product, wait):
        """
        CP-RF-07-01: Verificar que admin puede crear producto con datos válidos.

        Precondiciones:
        - Usuario es administrador logueado

        Pasos:
        1. Navegar a administración de catálogo
        2. Hacer clic en 'Crear Producto'
        3. Llenar formulario con datos válidos
        4. Hacer clic en 'Guardar'

        Resultado: Producto creado exitosamente
        """
        driver.get(f"{app_url}/admin/catalogo/crear")

        wait.until(EC.presence_of_element_located((By.ID, "titulo"))).send_keys(comic_product['titulo'])
        driver.find_element(By.ID, "autor").send_keys(comic_product['autor'])
        driver.find_element(By.ID, "editorial").send_keys(comic_product['editorial'])
        driver.find_element(By.ID, "precio").send_keys(str(comic_product['precio']))
        driver.find_element(By.ID, "stock").send_keys(str(comic_product['stock']))
        driver.find_element(By.ID, "descripcion").send_keys(comic_product['descripcion'])
        driver.find_element(By.ID, "categoria").send_keys(comic_product['categoria'])

        driver.find_element(By.ID, "btn-guardar").click()

        # Verificar redirección exitosa
        wait.until(EC.url_contains(f"{app_url}/admin/catalogo"))
        assert "crear" not in driver.current_url.lower()

    @pytest.mark.parametrize("campo_faltante", ["titulo", "autor", "precio", "stock"])
    def test_rf_07_02_creation_fails_with_missing_required_fields(self, driver, app_url, comic_product, wait, campo_faltante):
        """
        CP-RF-07-02: Verificar que creación falla si faltan campos requeridos.

        Campos requeridos:
        - Título
        - Autor
        - Precio
        - Stock
        """
        driver.get(f"{app_url}/admin/catalogo/crear")

        # Llenar todos excepto el campo faltante
        if campo_faltante != "titulo":
            wait.until(EC.presence_of_element_located((By.ID, "titulo"))).send_keys(comic_product['titulo'])
        if campo_faltante != "autor":
            driver.find_element(By.ID, "autor").send_keys(comic_product['autor'])
        if campo_faltante != "precio":
            driver.find_element(By.ID, "precio").send_keys(str(comic_product['precio']))
        if campo_faltante != "stock":
            driver.find_element(By.ID, "stock").send_keys(str(comic_product['stock']))

        driver.find_element(By.ID, "btn-guardar").click()

        # Debe mostrar error
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, f"error-{campo_faltante}")))
        assert "crear" in driver.current_url.lower()

    def test_rf_07_03_creation_fails_with_invalid_price(self, driver, app_url, comic_product, wait):
        """
        CP-RF-07-03: Verificar que precio inválido impide creación.
        """
        driver.get(f"{app_url}/admin/catalogo/crear")

        wait.until(EC.presence_of_element_located((By.ID, "titulo"))).send_keys(comic_product['titulo'])
        driver.find_element(By.ID, "autor").send_keys(comic_product['autor'])
        driver.find_element(By.ID, "precio").send_keys("-1000")  # Precio negativo
        driver.find_element(By.ID, "stock").send_keys(str(comic_product['stock']))

        driver.find_element(By.ID, "btn-guardar").click()

        # Debe mostrar error de validación
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error-precio")))


class TestUpdateProduct:
    """CP-RF-08: Actualizar producto (Admin)"""

    def test_rf_08_01_admin_can_update_product_with_valid_data(self, driver, app_url, wait):
        """
        CP-RF-08-01: Verificar que admin puede actualizar producto con datos válidos.

        Pasos:
        1. Navegar a edición de producto
        2. Modificar datos
        3. Guardar cambios

        Resultado: Producto actualizado exitosamente
        """
        driver.get(f"{app_url}/admin/catalogo/editar/1")

        wait.until(EC.presence_of_element_located((By.ID, "titulo")))

        # Limpiar y actualizar título
        titulo_field = driver.find_element(By.ID, "titulo")
        titulo_field.clear()
        titulo_field.send_keys("Título Actualizado v2")

        driver.find_element(By.ID, "btn-guardar").click()

        # Verificar que se guardó
        wait.until(EC.url_contains(f"{app_url}/admin/catalogo"))
        assert "editar" not in driver.current_url.lower()

    def test_rf_08_02_update_preserves_other_product_fields(self, driver, app_url, wait):
        """
        CP-RF-08-02: Verificar que actualizar un campo no afecta otros.
        """
        driver.get(f"{app_url}/admin/catalogo/editar/1")

        wait.until(EC.presence_of_element_located((By.ID, "titulo")))

        # Obtener valor original del autor
        autor_field = driver.find_element(By.ID, "autor")
        autor_original = autor_field.get_attribute("value")

        # Actualizar solo el título
        titulo_field = driver.find_element(By.ID, "titulo")
        titulo_field.clear()
        titulo_field.send_keys("Nuevo Título")

        driver.find_element(By.ID, "btn-guardar").click()

        # Volver a editar y verificar que el autor se mantiene
        driver.get(f"{app_url}/admin/catalogo/editar/1")
        wait.until(EC.presence_of_element_located((By.ID, "autor")))
        assert driver.find_element(By.ID, "autor").get_attribute("value") == autor_original

    def test_rf_08_03_update_fails_with_invalid_stock_value(self, driver, app_url, wait):
        """
        CP-RF-08-03: Verificar que stock inválido impide actualización.
        """
        driver.get(f"{app_url}/admin/catalogo/editar/1")

        wait.until(EC.presence_of_element_located((By.ID, "stock")))

        stock_field = driver.find_element(By.ID, "stock")
        stock_field.clear()
        stock_field.send_keys("-50")  # Stock negativo

        driver.find_element(By.ID, "btn-guardar").click()

        # Debe mostrar error
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error-stock")))


class TestDeleteProduct:
    """CP-RF-09: Eliminar producto (Admin)"""

    def test_rf_09_01_admin_can_delete_product(self, driver, app_url, wait):
        """
        CP-RF-09-01: Verificar que admin puede eliminar un producto.

        Pasos:
        1. Navegar a listado de productos
        2. Hacer clic en eliminar
        3. Confirmar eliminación

        Resultado: Producto eliminado del catálogo
        """
        driver.get(f"{app_url}/admin/catalogo")

        # Encontrar botón de eliminar
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "btn-eliminar")))
        btn_eliminar = driver.find_element(By.CLASS_NAME, "btn-eliminar")
        btn_eliminar.click()

        # Confirmar eliminación en diálogo
        wait.until(EC.presence_of_element_located((By.ID, "btn-confirmar-eliminar")))
        driver.find_element(By.ID, "btn-confirmar-eliminar").click()

        # Verificar que fue eliminado
        wait.until(EC.url_contains(f"{app_url}/admin/catalogo"))
        assert "eliminar" not in driver.page_source.lower()

    def test_rf_09_02_delete_requires_confirmation(self, driver, app_url, wait):
        """
        CP-RF-09-02: Verificar que eliminación requiere confirmación.
        """
        driver.get(f"{app_url}/admin/catalogo")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "btn-eliminar")))
        driver.find_element(By.CLASS_NAME, "btn-eliminar").click()

        # Debe aparecer diálogo de confirmación
        wait.until(EC.presence_of_element_located((By.ID, "modal-confirmar-eliminar")))
        assert driver.find_element(By.ID, "modal-confirmar-eliminar").is_displayed()

    def test_rf_09_03_cancel_delete_preserves_product(self, driver, app_url, wait):
        """
        CP-RF-09-03: Verificar que cancelar eliminación preserva el producto.
        """
        driver.get(f"{app_url}/admin/catalogo")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "btn-eliminar")))
        driver.find_element(By.CLASS_NAME, "btn-eliminar").click()

        # Clickear cancelar
        wait.until(EC.presence_of_element_located((By.ID, "btn-cancelar-eliminar")))
        driver.find_element(By.ID, "btn-cancelar-eliminar").click()

        # El modal debe cerrarse y el producto sigue en la lista
        assert not driver.find_element(By.ID, "modal-confirmar-eliminar").is_displayed()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "producto-item")))


class TestProductSearch:
    """CP-RF-10: Búsqueda de productos"""

    @pytest.mark.parametrize("keyword,expected_results_min", [
        ("Spider-Man", 1),
        ("Batman", 1),
        ("Marvel", 5),
        ("nacional", 2),
    ])
    def test_rf_10_01_search_returns_relevant_results(self, driver, app_url, wait, keyword, expected_results_min):
        """
        CP-RF-10-01: Verificar que búsqueda retorna resultados relevantes.

        Casos:
        - Búsqueda por título exacto
        - Búsqueda por tema
        - Búsqueda por editorial
        """
        driver.get(f"{app_url}/catalogo")

        # Ingresar término de búsqueda
        search_field = wait.until(EC.presence_of_element_located((By.ID, "buscar")))
        search_field.send_keys(keyword)
        search_field.send_keys("\n")  # Enter

        # Esperar resultados
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "producto-item")))
        productos = driver.find_elements(By.CLASS_NAME, "producto-item")

        assert len(productos) >= expected_results_min

    def test_rf_10_02_search_no_results_shows_message(self, driver, app_url, search_keywords, wait):
        """
        CP-RF-10-02: Verificar que búsqueda sin resultados muestra mensaje.
        """
        driver.get(f"{app_url}/catalogo")

        search_field = wait.until(EC.presence_of_element_located((By.ID, "buscar")))
        search_field.send_keys(search_keywords['no_existente'])
        search_field.send_keys("\n")

        # Debe mostrar mensaje de no resultados
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sin-resultados")))
        assert "no encontrado" in driver.page_source.lower() or "sin resultados" in driver.page_source.lower()

    def test_rf_10_03_search_is_case_insensitive(self, driver, app_url, wait):
        """
        CP-RF-10-03: Verificar que búsqueda no distingue mayúsculas.
        """
        driver.get(f"{app_url}/catalogo")

        # Buscar con minúsculas
        search_field = wait.until(EC.presence_of_element_located((By.ID, "buscar")))
        search_field.send_keys("spider-man")
        search_field.send_keys("\n")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "producto-item")))
        resultados_minusculas = driver.find_elements(By.CLASS_NAME, "producto-item")

        # Buscar con mayúsculas
        driver.get(f"{app_url}/catalogo")
        search_field = wait.until(EC.presence_of_element_located((By.ID, "buscar")))
        search_field.send_keys("SPIDER-MAN")
        search_field.send_keys("\n")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "producto-item")))
        resultados_mayusculas = driver.find_elements(By.CLASS_NAME, "producto-item")

        # Ambos deben tener resultados similares
        assert len(resultados_minusculas) == len(resultados_mayusculas)
