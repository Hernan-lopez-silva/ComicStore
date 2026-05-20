"""
Tests de Carrito de Compras y Checkout de ComicStore.
Cubre RF-03 (Agregar), RF-04 (Eliminar), RF-11 (Modificar cantidad),
RF-12 (Resumen/Checkout), RF-13 (Descuentos).
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


class TestAddToCart:
    """CP-RF-03: Agregar producto al carrito"""

    def test_rf_03_01_add_product_to_cart_with_valid_quantity(self, driver, app_url, wait):
        """
        CP-RF-03-01: Verificar que se puede agregar producto al carrito con cantidad válida.

        Precondiciones:
        - El producto está disponible
        - La cantidad solicitada está en stock

        Pasos:
        1. Navegar a detalle del producto
        2. Seleccionar cantidad
        3. Hacer clic en 'Agregar al carrito'

        Resultado: Producto agregado al carrito
        """
        driver.get(f"{app_url}/catalogo")

        # Seleccionar primer producto
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "producto-item"))).click()

        # Seleccionar cantidad
        wait.until(EC.presence_of_element_located((By.ID, "cantidad")))
        cantidad_field = driver.find_element(By.ID, "cantidad")
        cantidad_field.clear()
        cantidad_field.send_keys("2")

        # Agregar al carrito
        driver.find_element(By.ID, "btn-agregar-carrito").click()

        # Verificar confirmación
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "producto-agregado")))
        assert "agregado" in driver.page_source.lower()

    @pytest.mark.parametrize("cantidad", [1, 2, 5, 10, 50])
    def test_rf_03_02_add_product_with_various_valid_quantities(self, driver, app_url, wait, cantidad):
        """
        CP-RF-03-02: Verificar que se pueden agregar diferentes cantidades válidas.

        Cantidades válidas:
        - 1 unidad
        - 2 unidades
        - 5 unidades
        - 10 unidades
        - 50 unidades
        """
        driver.get(f"{app_url}/catalogo")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "producto-item"))).click()

        wait.until(EC.presence_of_element_located((By.ID, "cantidad")))
        cantidad_field = driver.find_element(By.ID, "cantidad")
        cantidad_field.clear()
        cantidad_field.send_keys(str(cantidad))

        driver.find_element(By.ID, "btn-agregar-carrito").click()

        # Verificar que se agregó
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "carrito-actualizado")))
        assert "carrito" in driver.page_source.lower()

    def test_rf_03_03_add_product_exceeding_stock_fails(self, driver, app_url, wait):
        """
        CP-RF-03-03: Verificar que agregar más que el stock disponible falla.
        """
        driver.get(f"{app_url}/catalogo")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "producto-item"))).click()

        # Obtener stock disponible
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "stock-disponible")))
        stock_text = driver.find_element(By.CLASS_NAME, "stock-disponible").text
        # Asumir formato "Stock: 50"
        stock_amount = int(''.join(filter(str.isdigit, stock_text.split(':')[-1])))

        # Intentar agregar más que el stock
        cantidad_field = driver.find_element(By.ID, "cantidad")
        cantidad_field.clear()
        cantidad_field.send_keys(str(stock_amount + 10))

        driver.find_element(By.ID, "btn-agregar-carrito").click()

        # Debe mostrar error
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error-stock-insuficiente")))


class TestRemoveFromCart:
    """CP-RF-04: Eliminar producto del carrito"""

    def test_rf_04_01_remove_product_from_cart(self, driver, app_url, wait):
        """
        CP-RF-04-01: Verificar que se puede eliminar un producto del carrito.

        Precondiciones:
        - El carrito contiene al menos un producto

        Pasos:
        1. Navegar al carrito
        2. Hacer clic en eliminar producto
        3. Confirmar eliminación

        Resultado: Producto removido del carrito
        """
        driver.get(f"{app_url}/carrito")

        # Verificar que hay productos en el carrito
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "item-carrito")))

        # Obtener cantidad de items inicial
        items_inicial = len(driver.find_elements(By.CLASS_NAME, "item-carrito"))

        # Eliminar primer item
        driver.find_element(By.CLASS_NAME, "btn-eliminar-item").click()

        # Confirmar eliminación
        wait.until(EC.presence_of_element_located((By.ID, "btn-confirmar-eliminar-item")))
        driver.find_element(By.ID, "btn-confirmar-eliminar-item").click()

        # Verificar que la cantidad disminuyó
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "carrito-actualizado")))
        items_actual = len(driver.find_elements(By.CLASS_NAME, "item-carrito"))
        assert items_actual == items_inicial - 1

    def test_rf_04_02_remove_all_items_empties_cart(self, driver, app_url, wait):
        """
        CP-RF-04-02: Verificar que eliminar todos los items vacía el carrito.
        """
        driver.get(f"{app_url}/carrito")

        # Eliminar todos los items
        while len(driver.find_elements(By.CLASS_NAME, "item-carrito")) > 0:
            driver.find_element(By.CLASS_NAME, "btn-eliminar-item").click()
            wait.until(EC.presence_of_element_located((By.ID, "btn-confirmar-eliminar-item")))
            driver.find_element(By.ID, "btn-confirmar-eliminar-item").click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "carrito-actualizado")))

        # Verificar que el carrito está vacío
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "carrito-vacio")))
        assert "carrito vacio" in driver.page_source.lower() or "sin productos" in driver.page_source.lower()

    def test_rf_04_03_cancel_delete_preserves_item(self, driver, app_url, wait):
        """
        CP-RF-04-03: Verificar que cancelar eliminación preserva el producto.
        """
        driver.get(f"{app_url}/carrito")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "item-carrito")))
        items_inicial = len(driver.find_elements(By.CLASS_NAME, "item-carrito"))

        # Intentar eliminar pero cancelar
        driver.find_element(By.CLASS_NAME, "btn-eliminar-item").click()
        wait.until(EC.presence_of_element_located((By.ID, "btn-cancelar-eliminar-item")))
        driver.find_element(By.ID, "btn-cancelar-eliminar-item").click()

        # Verificar que el item sigue en el carrito
        items_actual = len(driver.find_elements(By.CLASS_NAME, "item-carrito"))
        assert items_actual == items_inicial


class TestUpdateCartQuantity:
    """CP-RF-11: Modificar cantidad de productos en el carrito"""

    def test_rf_11_01_update_product_quantity_in_cart(self, driver, app_url, wait):
        """
        CP-RF-11-01: Verificar que se puede modificar cantidad en el carrito.

        Pasos:
        1. Navegar al carrito
        2. Modificar cantidad de un producto
        3. Verificar que se actualiza el total

        Resultado: Cantidad actualizada, total recalculado
        """
        driver.get(f"{app_url}/carrito")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "item-carrito")))

        # Obtener precio total inicial
        total_inicial = float(driver.find_element(By.CLASS_NAME, "total-carrito").text.split('$')[-1].replace(',', ''))

        # Cambiar cantidad
        cantidad_field = driver.find_element(By.CLASS_NAME, "cantidad-item")
        cantidad_field.clear()
        cantidad_field.send_keys("3")
        cantidad_field.send_keys(Keys.RETURN)

        # Esperar actualización
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "carrito-actualizado")))

        # Verificar que el total cambió
        total_nuevo = float(driver.find_element(By.CLASS_NAME, "total-carrito").text.split('$')[-1].replace(',', ''))
        assert total_nuevo > total_inicial

    @pytest.mark.parametrize("nueva_cantidad", [1, 2, 5, 10])
    def test_rf_11_02_update_with_various_quantities(self, driver, app_url, wait, nueva_cantidad):
        """
        CP-RF-11-02: Verificar que se pueden establecer diferentes cantidades.
        """
        driver.get(f"{app_url}/carrito")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "item-carrito")))

        cantidad_field = driver.find_element(By.CLASS_NAME, "cantidad-item")
        cantidad_field.clear()
        cantidad_field.send_keys(str(nueva_cantidad))
        cantidad_field.send_keys(Keys.RETURN)

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "carrito-actualizado")))
        assert str(nueva_cantidad) in cantidad_field.get_attribute("value")

    def test_rf_11_03_update_to_exceed_stock_fails(self, driver, app_url, wait):
        """
        CP-RF-11-03: Verificar que aumentar cantidad más allá del stock falla.
        """
        driver.get(f"{app_url}/carrito")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "item-carrito")))

        # Obtener stock disponible del producto
        stock_disponible = int(driver.find_element(By.CLASS_NAME, "stock-disponible-item").text.split(':')[-1].strip())

        cantidad_field = driver.find_element(By.CLASS_NAME, "cantidad-item")
        cantidad_field.clear()
        cantidad_field.send_keys(str(stock_disponible + 50))
        cantidad_field.send_keys(Keys.RETURN)

        # Debe mostrar error
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error-stock-insuficiente")))


class TestCheckout:
    """CP-RF-12: Resumen de pedido y checkout"""

    def test_rf_12_01_checkout_shows_order_summary(self, driver, app_url, wait, capture_screenshot):
        """
        CP-RF-12-01: Verificar que checkout muestra resumen del pedido.

        Pasos:
        1. Navegar al carrito
        2. Hacer clic en 'Proceder al Checkout'
        3. Verificar que se muestra resumen

        Resultado: Resumen del pedido visible con detalles
        """
        driver.get(f"{app_url}/carrito")
        capture_screenshot("paso1_carrito")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "item-carrito")))

        # Proceder a checkout
        driver.find_element(By.ID, "btn-checkout").click()

        # Verificar que se muestra resumen
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "resumen-pedido")))
        capture_screenshot("paso2_resumen_pedido")

        assert driver.find_element(By.CLASS_NAME, "subtotal")
        assert driver.find_element(By.CLASS_NAME, "impuestos")
        assert driver.find_element(By.CLASS_NAME, "total-final")

    def test_rf_12_02_checkout_allows_address_entry(self, driver, app_url, shipping_address, wait):
        """
        CP-RF-12-02: Verificar que se puede ingresar dirección de envío.
        """
        driver.get(f"{app_url}/carrito")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "item-carrito")))
        driver.find_element(By.ID, "btn-checkout").click()

        wait.until(EC.presence_of_element_located((By.ID, "direccion")))

        # Ingresar dirección
        driver.find_element(By.ID, "nombre").send_keys(shipping_address['nombre'])
        driver.find_element(By.ID, "direccion").send_keys(shipping_address['direccion'])
        driver.find_element(By.ID, "ciudad").send_keys(shipping_address['ciudad'])
        driver.find_element(By.ID, "codigo_postal").send_keys(shipping_address['codigo_postal'])
        driver.find_element(By.ID, "telefono").send_keys(shipping_address['telefono'])

        # Proceder al pago
        driver.find_element(By.ID, "btn-proceder-pago").click()

        # Debe proceder a la siguiente paso
        wait.until(EC.url_contains(f"{app_url}/checkout/pago"))

    def test_rf_12_03_checkout_displays_correct_totals(self, driver, app_url, wait):
        """
        CP-RF-12-03: Verificar que los totales se calculan correctamente.
        """
        driver.get(f"{app_url}/carrito")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "item-carrito")))

        # Obtener totales del carrito
        subtotal_carrito = float(driver.find_element(By.CLASS_NAME, "subtotal-carrito").text.split('$')[-1].replace(',', ''))

        driver.find_element(By.ID, "btn-checkout").click()

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "resumen-pedido")))

        # Obtener subtotal en checkout
        subtotal_checkout = float(driver.find_element(By.CLASS_NAME, "subtotal").text.split('$')[-1].replace(',', ''))

        # Deben ser iguales
        assert subtotal_carrito == subtotal_checkout


class TestDiscounts:
    """CP-RF-13: Aplicar descuentos con cupones"""

    def test_rf_13_01_apply_valid_coupon_to_cart(self, driver, app_url, coupon_data, wait):
        """
        CP-RF-13-01: Verificar que se puede aplicar un cupón válido.

        Precondiciones:
        - El cupón existe y es válido
        - El carrito no está vacío

        Pasos:
        1. Navegar al carrito
        2. Ingresar código de cupón
        3. Hacer clic en 'Aplicar Cupón'

        Resultado: Cupón aplicado, descuento reflejado en total
        """
        driver.get(f"{app_url}/carrito")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "item-carrito")))

        # Obtener total original
        total_original = float(driver.find_element(By.CLASS_NAME, "total-carrito").text.split('$')[-1].replace(',', ''))

        # Ingresar cupón
        coupon_field = wait.until(EC.presence_of_element_located((By.ID, "codigo-cupon")))
        coupon_field.send_keys(coupon_data['valido'])

        driver.find_element(By.ID, "btn-aplicar-cupon").click()

        # Verificar que el descuento se aplicó
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cupon-aplicado")))
        total_nuevo = float(driver.find_element(By.CLASS_NAME, "total-carrito").text.split('$')[-1].replace(',', ''))

        assert total_nuevo < total_original
        assert "20%" in driver.page_source or "-20%" in driver.page_source

    def test_rf_13_02_invalid_coupon_shows_error(self, driver, app_url, coupon_data, wait):
        """
        CP-RF-13-02: Verificar que cupón inválido muestra error.
        """
        driver.get(f"{app_url}/carrito")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "item-carrito")))

        coupon_field = wait.until(EC.presence_of_element_located((By.ID, "codigo-cupon")))
        coupon_field.send_keys(coupon_data['no_existente'])

        driver.find_element(By.ID, "btn-aplicar-cupon").click()

        # Debe mostrar error
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error-cupon")))
        assert "invalido" in driver.page_source.lower() or "no valido" in driver.page_source.lower()

    def test_rf_13_03_expired_coupon_cannot_be_applied(self, driver, app_url, coupon_data, wait):
        """
        CP-RF-13-03: Verificar que cupón expirado no se puede aplicar.
        """
        driver.get(f"{app_url}/carrito")

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "item-carrito")))

        coupon_field = wait.until(EC.presence_of_element_located((By.ID, "codigo-cupon")))
        coupon_field.send_keys(coupon_data['expirado'])

        driver.find_element(By.ID, "btn-aplicar-cupon").click()

        # Debe mostrar error de expiración
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error-cupon-expirado")))
        assert "expirado" in driver.page_source.lower()
