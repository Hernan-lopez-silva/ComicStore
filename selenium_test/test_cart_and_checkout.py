"""
Tests de Carrito de Compras y Checkout de ComicStore.
Adaptados a los templates reales de la aplicación.

IDs reales en carrito.html:
  - #mensajeCarritoVacio (div vacío)
  - #tabla (contenedor de la tabla)
  - #mostrarCarrito (tbody, poblado por JS)
  - #totalCarrito (total en tfoot)
  - #btnCheckout (enlace a /carrito/checkout/)

IDs reales en checkout.html:
  - #name, #email, #phone, #address, #city, #region, #postal_code
  - #couponInput, #btnApplyCoupon
  - #summarySubtotal, #summaryTotal, #summaryDiscount, #discountRow
  - #btnProcessOrder
  - #couponMessage (mensajes de cupón)
  - #orderSummary (resumen cargado via JS)

Cubre RF-03 (Agregar), RF-04 (Eliminar), RF-11 (Modificar cantidad),
RF-12 (Resumen/Checkout), RF-13 (Descuentos).
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time


def js_click(driver, element):
    """Hace clic via JavaScript para evitar ElementClickInterceptedException."""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.2)
    driver.execute_script("arguments[0].click();", element)


# ============================================================================
# HELPER: navegar al primer producto y añadir al carrito
# ============================================================================

def add_first_product_to_cart(driver, app_url, wait):
    """Navega al primer producto disponible y lo añade al carrito."""
    driver.get(f"{app_url}/")

    # Esperar que cargue el landing
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".galeria")))
    botones = driver.find_elements(By.CSS_SELECTOR, "button.btn-dark")
    if not botones:
        return False  # No hay productos

    comprar_btn = botones[0]
    js_click(driver, comprar_btn)

    # Esperar que se cargue la página del producto
    wait.until(EC.presence_of_element_located((By.ID, "carro")))
    carro_btn = driver.find_element(By.ID, "carro")
    js_click(driver, carro_btn)

    # Esperar modal de confirmación y luego ir al carrito
    wait.until(EC.visibility_of_element_located((By.ID, "exampleModal")))
    ir_carro_btn = wait.until(EC.element_to_be_clickable((By.ID, "irCarro")))
    js_click(driver, ir_carro_btn)

    # Esperar que cargue el carrito
    wait.until(EC.presence_of_element_located((By.ID, "tabla")))
    time.sleep(1.5)  # JS necesita tiempo para poblar el carrito desde localStorage
    return True


# ============================================================================
# CLASE: Agregar producto al carrito
# ============================================================================

class TestAddToCart:
    """CP-RF-03: Agregar producto al carrito"""

    def test_rf_03_01_add_product_to_cart_via_product_page(
        self, driver, app_url, wait
    ):
        """
        CP-RF-03-01: Verificar que se puede agregar un producto al carrito.

        Pasos:
        1. Ir al landing, hacer clic en 'Comprar' del primer producto
        2. En la página del producto, hacer clic en 'Añadir al Carrito'
        3. Verificar que aparece el modal de éxito

        Resultado: Modal #exampleModal aparece confirmando el agregado
        """
        driver.get(f"{app_url}/")

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".galeria")))
        botones = driver.find_elements(By.CSS_SELECTOR, "button.btn-dark")
        if not botones:
            pytest.skip("No hay productos en la BD")

        comprar_btn = botones[0]
        js_click(driver, comprar_btn)

        wait.until(EC.presence_of_element_located((By.ID, "carro")))
        assert driver.find_element(By.ID, "cantidadInput").get_attribute("value") == "1", \
            "La cantidad por defecto debe ser 1"

        carro_btn = driver.find_element(By.ID, "carro")
        js_click(driver, carro_btn)

        # Debe aparecer el modal de éxito
        wait.until(EC.visibility_of_element_located((By.ID, "exampleModal")))
        modal = driver.find_element(By.ID, "exampleModal")
        assert modal.is_displayed(), "El modal de producto agregado debe aparecer"

    def test_rf_03_02_product_page_has_quantity_controls(
        self, driver, app_url, wait
    ):
        """
        CP-RF-03-02: Verificar que la página de producto tiene controles de cantidad.
        Los botones +/- (btnMas, btnMenos) y el input cantidadInput deben existir.
        """
        driver.get(f"{app_url}/producto/?id=1")

        if "producto" not in driver.current_url.lower():
            pytest.skip("El producto con id=1 no existe en la BD")

        wait.until(EC.presence_of_element_located((By.ID, "cantidadInput")))
        assert driver.find_element(By.ID, "btnMas")
        assert driver.find_element(By.ID, "btnMenos")
        assert driver.find_element(By.ID, "cantidadInput")

    def test_rf_03_03_quantity_increase_button_works(
        self, driver, app_url, wait
    ):
        """
        CP-RF-03-03: Verificar que el botón '+' incrementa la cantidad.
        """
        driver.get(f"{app_url}/producto/?id=1")

        if "producto" not in driver.current_url.lower():
            pytest.skip("El producto con id=1 no existe en la BD")

        wait.until(EC.presence_of_element_located((By.ID, "cantidadInput")))
        cantidad_inicial = int(driver.find_element(By.ID, "cantidadInput").get_attribute("value"))

        driver.find_element(By.ID, "btnMas").click()
        time.sleep(0.3)

        cantidad_nueva = int(driver.find_element(By.ID, "cantidadInput").get_attribute("value"))
        assert cantidad_nueva == cantidad_inicial + 1, \
            f"La cantidad debe incrementar de {cantidad_inicial} a {cantidad_inicial + 1}"

    def test_rf_03_04_modal_has_ir_al_carrito_button(
        self, driver, app_url, wait
    ):
        """
        CP-RF-03-04: Verificar que el modal tiene botón 'Ir al carrito'.
        """
        driver.get(f"{app_url}/producto/?id=1")

        if "producto" not in driver.current_url.lower():
            pytest.skip("El producto con id=1 no existe en la BD")

        wait.until(EC.presence_of_element_located((By.ID, "carro")))
        driver.find_element(By.ID, "carro").click()
        wait.until(EC.visibility_of_element_located((By.ID, "exampleModal")))

        assert driver.find_element(By.ID, "irCarro"), "Debe haber botón 'Ir al carrito'"
        assert driver.find_element(By.ID, "seguirComprando"), "Debe haber botón 'Seguir comprando'"


# ============================================================================
# CLASE: Carrito de compras
# ============================================================================

class TestCart:
    """CP-RF-04/RF-11: Carrito de compras"""

    def test_rf_04_01_cart_page_loads_correctly(
        self, driver, app_url, wait
    ):
        """
        CP-RF-04-01: Verificar que la página del carrito carga correctamente.
        """
        driver.get(f"{app_url}/carrito/")

        wait.until(EC.presence_of_element_located((By.ID, "tabla")))
        assert driver.find_element(By.ID, "totalCarrito") is not None, \
            "El carrito debe tener el elemento de total"
        assert driver.find_element(By.ID, "btnCheckout") is not None, \
            "El carrito debe tener el botón de checkout"

    def test_rf_04_02_cart_checkout_button_links_to_checkout(
        self, driver, app_url, wait
    ):
        """
        CP-RF-04-02: Verificar que el botón 'Proceder al Pago' lleva al checkout.
        """
        driver.get(f"{app_url}/carrito/")
        wait.until(EC.presence_of_element_located((By.ID, "btnCheckout")))

        btn = driver.find_element(By.ID, "btnCheckout")
        href = btn.get_attribute("href")
        assert "checkout" in href.lower(), \
            f"El botón de checkout debe apuntar a /checkout/, pero apunta a: {href}"

    def test_rf_04_03_add_product_and_verify_cart_has_items(
        self, driver, app_url, wait
    ):
        """
        CP-RF-04-03: Verificar que después de agregar un producto, el carrito no está vacío.
        El carrito se gestiona con localStorage/JS.
        """
        added = add_first_product_to_cart(driver, app_url, wait)
        if not added:
            pytest.skip("No hay productos en la BD para agregar al carrito")

        # El carrito se llena por JS desde localStorage
        # Verificar que aparece el tbody con datos
        time.sleep(1.5)
        tbody = driver.find_element(By.ID, "mostrarCarrito")
        rows = tbody.find_elements(By.TAG_NAME, "tr")
        assert len(rows) >= 1, "El carrito debe tener al menos 1 fila de producto"


# ============================================================================
# CLASE: Checkout
# ============================================================================

class TestCheckout:
    """CP-RF-12: Resumen de pedido y checkout"""

    def test_rf_12_01_checkout_page_loads_correctly(
        self, driver, app_url, wait, capture_screenshot
    ):
        """
        CP-RF-12-01: Verificar que la página de checkout carga correctamente
        con todos sus elementos.

        Pasos:
        1. Navegar directamente a /carrito/checkout/
        2. Verificar elementos del formulario de envío

        Resultado: Formulario de checkout visible con campos reales
        """
        driver.get(f"{app_url}/carrito/checkout/")
        capture_screenshot("paso1_checkout")

        wait.until(EC.presence_of_element_located((By.ID, "checkoutForm")))

        assert driver.find_element(By.ID, "name")
        assert driver.find_element(By.ID, "email")
        assert driver.find_element(By.ID, "address")
        assert driver.find_element(By.ID, "city")
        assert driver.find_element(By.ID, "region")
        assert driver.find_element(By.ID, "btnProcessOrder")

    def test_rf_12_02_checkout_has_order_summary(
        self, driver, app_url, wait
    ):
        """
        CP-RF-12-02: Verificar que el checkout muestra el resumen del pedido.
        """
        driver.get(f"{app_url}/carrito/checkout/")
        wait.until(EC.presence_of_element_located((By.ID, "orderSummary")))

        assert driver.find_element(By.ID, "summarySubtotal")
        assert driver.find_element(By.ID, "summaryTotal")

    def test_rf_12_03_checkout_shipping_form_is_fillable(
        self, driver, app_url, shipping_address, wait
    ):
        """
        CP-RF-12-03: Verificar que se puede llenar el formulario de envío.
        """
        driver.get(f"{app_url}/carrito/checkout/")
        wait.until(EC.presence_of_element_located((By.ID, "checkoutForm")))

        name_field = driver.find_element(By.ID, "name")
        name_field.clear()
        name_field.send_keys(shipping_address['name'])

        email_field = driver.find_element(By.ID, "email")
        email_field.clear()
        email_field.send_keys(shipping_address['email'])

        address_field = driver.find_element(By.ID, "address")
        address_field.clear()
        address_field.send_keys(shipping_address['address'])

        city_field = driver.find_element(By.ID, "city")
        city_field.clear()
        city_field.send_keys(shipping_address['city'])

        region_select = Select(driver.find_element(By.ID, "region"))
        region_select.select_by_visible_text("Región Metropolitana")

        assert name_field.get_attribute("value") == shipping_address['name']
        assert email_field.get_attribute("value") == shipping_address['email']
        assert city_field.get_attribute("value") == shipping_address['city']

    def test_rf_12_04_checkout_has_payment_gateway_options(
        self, driver, app_url, wait
    ):
        """
        CP-RF-12-04: Verificar que el checkout muestra opciones de pasarela de pago.
        """
        driver.get(f"{app_url}/carrito/checkout/")
        wait.until(EC.presence_of_element_located((By.ID, "paymentGateways")))

        gateways = driver.find_elements(By.CSS_SELECTOR, "input[name='payment_gateway']")
        assert len(gateways) >= 1, \
            "Debe haber al menos 1 opción de pasarela de pago"


# ============================================================================
# CLASE: Cupones de descuento
# ============================================================================

class TestDiscounts:
    """CP-RF-13: Aplicar descuentos con cupones"""

    def test_rf_13_01_coupon_input_exists_in_checkout(
        self, driver, app_url, wait
    ):
        """
        CP-RF-13-01: Verificar que existe el campo de cupón en el checkout.
        """
        driver.get(f"{app_url}/carrito/checkout/")
        wait.until(EC.presence_of_element_located((By.ID, "couponInput")))

        assert driver.find_element(By.ID, "couponInput")
        assert driver.find_element(By.ID, "btnApplyCoupon")

    def test_rf_13_02_apply_valid_coupon_shows_discount(
        self, driver, app_url, coupon_data, wait
    ):
        """
        CP-RF-13-02: Verificar que aplicar el cupón 'COMICSTORE1' muestra un descuento.
        Este cupón está en el banner de la landing: 10% de descuento.
        """
        driver.get(f"{app_url}/carrito/checkout/")
        wait.until(EC.presence_of_element_located((By.ID, "couponInput")))

        coupon_input = driver.find_element(By.ID, "couponInput")
        coupon_input.clear()
        coupon_input.send_keys(coupon_data['valido'])

        btn = driver.find_element(By.ID, "btnApplyCoupon")
        js_click(driver, btn)

        # Esperar respuesta (el botón actualiza #couponMessage o #discountRow)
        time.sleep(1.5)

        coupon_msg = driver.find_element(By.ID, "couponMessage")
        discount_row = driver.find_element(By.ID, "discountRow")

        # Al menos uno de los dos debe estar visible/activo
        assert (
            coupon_msg.is_displayed()
            or "d-none" not in discount_row.get_attribute("class")
        ), "Al aplicar cupón válido debe aparecer mensaje o fila de descuento"

    def test_rf_13_03_apply_invalid_coupon_shows_error(
        self, driver, app_url, coupon_data, wait
    ):
        """
        CP-RF-13-03: Verificar que un cupón inválido muestra mensaje de error.
        """
        driver.get(f"{app_url}/carrito/checkout/")
        wait.until(EC.presence_of_element_located((By.ID, "couponInput")))

        coupon_input = driver.find_element(By.ID, "couponInput")
        coupon_input.clear()
        coupon_input.send_keys(coupon_data['no_existente'])

        btn = driver.find_element(By.ID, "btnApplyCoupon")
        js_click(driver, btn)

        time.sleep(1.5)

        coupon_msg = driver.find_element(By.ID, "couponMessage")
        assert coupon_msg.is_displayed(), \
            "Al aplicar cupón inválido debe aparecer mensaje de error"
        msg_text = coupon_msg.text.lower()
        assert (
            "inválido" in msg_text
            or "invalido" in msg_text
            or "no encontrado" in msg_text
            or "no existe" in msg_text
            or "incorrecto" in msg_text
        ), f"El mensaje de error debe indicar cupón inválido. Texto: '{msg_text}'"
