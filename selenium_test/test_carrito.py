"""
Pruebas automatizadas Selenium — Carrito de Compras ComicStore.

Cubre los requerimientos funcionales:
  - RF-03: Agregar producto al carrito
  - RF-04: Eliminar producto del carrito

Casos de prueba según documento Casos_de_Prueba_ComicStore_Corregido.docx:
  CP-RF-03-01  Agregar un cómic al carrito con sesión activa (APROBADO)
  CP-RF-03-02  Agregar el mismo cómic dos veces incrementa cantidad (APROBADO)
  CP-RF-03-03  Usuario no autenticado ve modal de login y no puede agregar al carrito (APROBADO)
  CP-RF-03-03b Botón del modal redirige a la página de inicio de sesión (APROBADO)
  CP-RF-04-01  Eliminar un producto del carrito actualiza el carrito (XFAIL)
  CP-RF-04-02  Eliminar el único producto deja el carrito vacío (XFAIL)
  CP-RF-04-03  El total se recalcula al eliminar uno de varios productos (XFAIL)

Selectores reales de la app:
  Landing       : #comics .card button  (botón "Comprar")
  Detalle prod  : #cantidadInput, #carro (añadir), #exampleModal (éxito)
  Carrito       : /carrito/ → #mostrarCarrito (tbody renderizado por JS),
                  #totalCarrito, #tituloCarro, #mensajeCarritoVacio, #btnCheckout
  Eliminar item : <i class="fa-trash-can" id="{product_id}"> (JS encadenado)

Notas técnicas sobre defectos conocidos:
  - CP-RF-03-03: La funcionalidad está correctamente implementada. producto.html
    muestra #btnLoginRequerido para usuarios no autenticados (en vez de #carro),
    y scriptProducto.js dispara el modal #modalLoginRequerido al hacer clic.
  - DEFECTO CP-RF-04-xx: scriptCarro.js referencia document.getElementById('btnPago')
    que no existe en carrito.html (la plantilla usa id='btnCheckout'). Esto provoca un
    TypeError en el callback DOMContentLoaded que cancela el registro de todos los
    event listeners definidos después de esa línea, incluyendo el listener del ícono
    .fa-trash-can. Como resultado, hacer clic en el ícono de eliminar no tiene efecto.
"""

import json
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


# ============================================================================
# HELPERS LOCALES
# ============================================================================

def _login(driver, wait, app_url, username, password):
    """Inicia sesión y espera que aparezca el dropdown del usuario autenticado."""
    driver.get(f"{app_url}/login/")
    wait.until(EC.presence_of_element_located((By.ID, "id_username"))).send_keys(username)
    campo_password = driver.find_element(By.ID, "id_password")
    campo_password.send_keys(password)
    campo_password.send_keys(Keys.RETURN)
    wait.until(EC.presence_of_element_located((By.ID, "dropdownMenuButton")))


def _agregar_primer_producto_via_ui(driver, wait, app_url, cantidad=1):
    """
    Navega al landing, hace clic en el primer cómic disponible,
    ajusta la cantidad y pulsa 'Añadir al Carrito'.

    Devuelve el título del cómic agregado (texto de #titleComic).
    """
    driver.get(f"{app_url}/")
    btn_comprar = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#comics .card button")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_comprar)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", btn_comprar)

    # Página de detalle del producto
    wait.until(EC.presence_of_element_located((By.ID, "cantidadInput")))
    titulo = driver.find_element(By.ID, "titleComic").text
    precio_texto = driver.find_element(By.ID, "priceComic").text  # "Precio: $XXXX"

    qty_field = driver.find_element(By.ID, "cantidadInput")
    qty_field.clear()
    qty_field.send_keys(str(cantidad))

    btn_carro = driver.find_element(By.ID, "carro")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_carro)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", btn_carro)

    # Esperar modal de confirmación
    wait.until(EC.visibility_of_element_located((By.ID, "exampleModal")))

    return titulo, precio_texto


def _inyectar_carrito(driver, app_url, items):
    """
    Inyecta ítems directamente en localStorage['cart'] sin pasar por la UI.

    items: lista de dicts con claves id, title, price, img, quantity.
    Requiere que el driver ya esté en una página de la misma origin (app_url).
    """
    driver.get(f"{app_url}/carrito/")
    driver.execute_script(
        "localStorage.setItem('cart', arguments[0]);",
        json.dumps(items)
    )


def _leer_carrito(driver):
    """Devuelve la lista de ítems en localStorage['cart'] (puede ser None)."""
    raw = driver.execute_script("return localStorage.getItem('cart');")
    if raw is None:
        return []
    return json.loads(raw)


# ============================================================================
# RF-03 — AGREGAR PRODUCTO AL CARRITO
# ============================================================================

class TestAgregarAlCarrito:
    """Casos de prueba CP-RF-03-xx: Agregar producto al carrito."""

    def test_cp_rf_03_01_agregar_comic_autenticado_actualiza_carrito(
        self, driver, app_url, existing_user_credentials, wait, capture_screenshot
    ):
        """
        CP-RF-03-01 — Verificar que el usuario puede agregar un cómic al carrito
        y este se actualiza con precio y cantidad.

        Precondiciones:
          - El usuario está autenticado en el sistema.
          - Existe al menos un cómic disponible en el catálogo.
          - El carrito del usuario está vacío.

        Pasos:
          1. Navegar al catálogo de productos.
          2. Seleccionar un cómic disponible.
          3. Hacer clic en 'Añadir al Carrito'.
          4. Verificar que el modal de confirmación se muestra.
          5. Ir a /carrito/ y verificar que el ítem aparece.

        Resultado esperado:
          El cómic aparece en el carrito con precio y cantidad correctos.

        Veredicto original: APROBADO.
        """
        # Paso 0: autenticar
        _login(
            driver, wait, app_url,
            existing_user_credentials["username"],
            existing_user_credentials["password"],
        )
        capture_screenshot("cp_rf_03_01_paso1_autenticado")

        # Pasos 1–3: navegar al producto y agregar al carrito
        titulo, precio_texto = _agregar_primer_producto_via_ui(driver, wait, app_url)
        capture_screenshot("cp_rf_03_01_paso2_modal_confirmacion")

        # Paso 4: verificar modal de éxito
        modal = driver.find_element(By.ID, "exampleModal")
        assert modal.is_displayed(), (
            "CP-RF-03-01: El modal de confirmación no se mostró tras agregar el producto."
        )

        # Paso 5: ir al carrito y verificar ítem
        driver.get(f"{app_url}/carrito/")
        time.sleep(1)  # scriptCarro.js renderiza desde localStorage
        capture_screenshot("cp_rf_03_01_paso3_carrito")

        carrito = _leer_carrito(driver)
        assert len(carrito) > 0, (
            "CP-RF-03-01: localStorage['cart'] está vacío después de agregar un producto."
        )
        # Verificar que el precio y título están registrados
        item = carrito[0]
        assert "title" in item and item["title"], (
            "CP-RF-03-01: El ítem en el carrito no tiene campo 'title'."
        )
        assert "price" in item and item["price"] > 0, (
            "CP-RF-03-01: El ítem en el carrito no tiene precio válido."
        )
        assert "quantity" in item and item["quantity"] > 0, (
            "CP-RF-03-01: El ítem en el carrito no tiene cantidad válida."
        )

        # Verificar que la tabla del carrito renderizó el ítem
        filas = driver.find_elements(By.CSS_SELECTOR, "#mostrarCarrito tr")
        assert len(filas) > 0, (
            "CP-RF-03-01: La tabla del carrito no muestra ningún ítem."
        )

    def test_cp_rf_03_02_agregar_mismo_comic_dos_veces_incrementa_cantidad(
        self, driver, app_url, existing_user_credentials, wait, capture_screenshot
    ):
        """
        CP-RF-03-02 — Verificar que agregar el mismo cómic dos veces incrementa
        la cantidad en lugar de duplicar la entrada.

        Precondiciones:
          - El usuario está autenticado.
          - Un cómic ya ha sido agregado al carrito.

        Pasos:
          1. Agregar un cómic (cantidad 1) al carrito.
          2. Agregar el mismo cómic una segunda vez (cantidad 1).
          3. Ir al carrito y verificar que hay una sola entrada con cantidad = 2.

        Resultado esperado:
          El carrito muestra 1 fila con quantity=2, no 2 filas separadas.

        Veredicto original: APROBADO.
        """
        _login(
            driver, wait, app_url,
            existing_user_credentials["username"],
            existing_user_credentials["password"],
        )

        # Primera adición
        titulo1, _ = _agregar_primer_producto_via_ui(driver, wait, app_url, cantidad=1)
        capture_screenshot("cp_rf_03_02_paso1_primera_adicion")

        # Segunda adición del mismo cómic (volver al landing y elegir el mismo)
        _agregar_primer_producto_via_ui(driver, wait, app_url, cantidad=1)
        capture_screenshot("cp_rf_03_02_paso2_segunda_adicion")

        # Verificar en localStorage
        driver.get(f"{app_url}/carrito/")
        time.sleep(1)
        carrito = _leer_carrito(driver)
        capture_screenshot("cp_rf_03_02_paso3_carrito")

        # Buscar el ítem con el mismo título
        items_con_titulo = [item for item in carrito if item.get("title") == titulo1]

        assert len(items_con_titulo) == 1, (
            f"CP-RF-03-02: Se esperaba 1 entrada para '{titulo1}', "
            f"pero se encontraron {len(items_con_titulo)} entradas duplicadas."
        )
        assert items_con_titulo[0]["quantity"] == 2, (
            f"CP-RF-03-02: Se esperaba quantity=2 pero se obtuvo "
            f"quantity={items_con_titulo[0]['quantity']}."
        )

    def test_cp_rf_03_03_usuario_no_autenticado_ve_modal_login(
        self, driver, app_url, wait, capture_screenshot
    ):
        """
        CP-RF-03-03 — Verificar que un usuario no autenticado al intentar agregar
        un producto al carrito ve un modal que le indica que debe iniciar sesión,
        y que el producto NO se agrega al carrito.

        Precondiciones:
          - El usuario NO ha iniciado sesión.
          - El catálogo tiene productos disponibles.

        Pasos:
          1. Navegar al catálogo sin iniciar sesión.
          2. Seleccionar un cómic (página de detalle del producto).
          3. Verificar que el botón visible es #btnLoginRequerido (no #carro).
          4. Hacer clic en el botón 'Añadir al Carrito'.
          5. Verificar que se muestra el modal #modalLoginRequerido.
          6. Verificar que el modal contiene el mensaje de sesión requerida.
          7. Verificar que el enlace del modal apunta a la URL de login.
          8. Verificar que el carrito (localStorage) sigue vacío.
          9. Hacer clic en 'Cancelar' y verificar que el modal se cierra.

        Resultado esperado:
          - El modal aparece con el mensaje correcto.
          - El producto NO se agrega a localStorage.
          - El enlace de login está presente y apunta a /login/.
          - El botón cancelar cierra el modal.

        Veredicto: APROBADO — la funcionalidad está implementada en producto.html
        y scriptProducto.js mediante #btnLoginRequerido y #modalLoginRequerido.
        """
        # Paso 1: sin sesión activa
        capture_screenshot("cp_rf_03_03_paso1_sin_sesion")

        # Paso 2: navegar al catálogo y entrar al primer producto
        driver.get(f"{app_url}/")
        btn_comprar = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#comics .card button")
            )
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", btn_comprar
        )
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", btn_comprar)

        wait.until(EC.presence_of_element_located((By.ID, "cantidadInput")))
        capture_screenshot("cp_rf_03_03_paso2_pagina_producto")

        # Paso 3: verificar que el botón es #btnLoginRequerido, NO #carro
        btn_login_requerido = driver.find_element(By.ID, "btnLoginRequerido")
        assert btn_login_requerido.is_displayed(), (
            "CP-RF-03-03: El botón #btnLoginRequerido no está visible para "
            "usuario no autenticado."
        )
        btns_carro = driver.find_elements(By.ID, "carro")
        assert len(btns_carro) == 0, (
            "CP-RF-03-03: El botón #carro (añadir al carrito directo) NO debería "
            "existir para usuarios no autenticados."
        )

        # Paso 4: hacer clic en el botón
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", btn_login_requerido
        )
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", btn_login_requerido)

        # Paso 5: verificar que el modal #modalLoginRequerido se muestra
        modal = wait.until(
            EC.visibility_of_element_located((By.ID, "modalLoginRequerido"))
        )
        capture_screenshot("cp_rf_03_03_paso3_modal_visible")
        assert modal.is_displayed(), (
            "CP-RF-03-03: El modal #modalLoginRequerido no se mostró tras hacer "
            "clic en el botón 'Añadir al Carrito' sin sesión activa."
        )

        # Paso 6: verificar que el modal contiene el mensaje adecuado
        cuerpo_modal = driver.find_element(By.CSS_SELECTOR, "#modalLoginRequerido .modal-body")
        texto_modal = cuerpo_modal.text.lower()
        assert "agregar" in texto_modal or "carrito" in texto_modal or "cuenta" in texto_modal, (
            f"CP-RF-03-03: El modal no contiene el mensaje esperado. "
            f"Texto encontrado: '{cuerpo_modal.text}'"
        )

        # Paso 7: verificar que el enlace de inicio de sesión apunta a /login/
        enlace_login = driver.find_element(
            By.CSS_SELECTOR, "#modalLoginRequerido a.btn-primary"
        )
        href = enlace_login.get_attribute("href")
        assert "/login/" in href, (
            f"CP-RF-03-03: El enlace del modal no apunta a la página de login. "
            f"href encontrado: '{href}'"
        )

        # Paso 8: verificar que el carrito sigue vacío (ningún producto fue agregado)
        carrito = _leer_carrito(driver)
        assert len(carrito) == 0, (
            "CP-RF-03-03: El producto fue agregado a localStorage a pesar de que "
            "el usuario no está autenticado."
        )

        # Paso 9: cerrar el modal con el botón Cancelar
        btn_cancelar = driver.find_element(
            By.CSS_SELECTOR, "#modalLoginRequerido .btn-secondary.btnClose"
        )
        driver.execute_script("arguments[0].click();", btn_cancelar)
        time.sleep(0.5)
        capture_screenshot("cp_rf_03_03_paso4_modal_cerrado")

        modal_tras_cerrar = driver.find_element(By.ID, "modalLoginRequerido")
        assert not modal_tras_cerrar.is_displayed(), (
            "CP-RF-03-03: El modal no se cerró al hacer clic en 'Cancelar'."
        )

    def test_cp_rf_03_03b_modal_login_redirige_a_login(
        self, driver, app_url, wait, capture_screenshot
    ):
        """
        CP-RF-03-03b — Verificar que al hacer clic en 'Iniciar sesión' dentro del
        modal, el navegador redirige efectivamente a la página de login.

        Precondiciones:
          - El usuario NO ha iniciado sesión.
          - El modal #modalLoginRequerido está visible (derivado de CP-RF-03-03).

        Pasos:
          1. Navegar a la página de un producto sin sesión.
          2. Hacer clic en #btnLoginRequerido para abrir el modal.
          3. Hacer clic en el enlace 'Iniciar sesión' del modal.
          4. Verificar que la URL resultante contiene /login/.

        Resultado esperado:
          El navegador navega a la página de inicio de sesión.
        """
        # Sin sesión activa — ir directo al primer producto
        driver.get(f"{app_url}/")
        btn_comprar = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#comics .card button")
            )
        )
        driver.execute_script("arguments[0].click();", btn_comprar)
        wait.until(EC.presence_of_element_located((By.ID, "btnLoginRequerido")))
        capture_screenshot("cp_rf_03_03b_paso1_producto")

        # Abrir el modal
        btn_login_requerido = driver.find_element(By.ID, "btnLoginRequerido")
        driver.execute_script("arguments[0].click();", btn_login_requerido)
        wait.until(EC.visibility_of_element_located((By.ID, "modalLoginRequerido")))
        capture_screenshot("cp_rf_03_03b_paso2_modal_abierto")

        # Clic en "Iniciar sesión"
        enlace_login = driver.find_element(
            By.CSS_SELECTOR, "#modalLoginRequerido a.btn-primary"
        )
        enlace_login.click()

        # Verificar redirección al login
        wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        capture_screenshot("cp_rf_03_03b_paso3_pagina_login")

        assert "/login/" in driver.current_url, (
            f"CP-RF-03-03b: Se esperaba navegar a /login/, pero la URL actual es "
            f"'{driver.current_url}'."
        )


# ============================================================================
# RF-04 — ELIMINAR PRODUCTO DEL CARRITO
# ============================================================================

class TestEliminarDelCarrito:
    """
    Casos de prueba CP-RF-04-xx: Eliminar producto del carrito.

    NOTA SOBRE EL DEFECTO SUBYACENTE:
    scriptCarro.js registra los event listeners dentro del callback DOMContentLoaded.
    La primera instrucción tras showCart() es:
        document.getElementById('btnPago').addEventListener('click', ...)
    El elemento '#btnPago' NO existe en carrito.html (el template usa '#btnCheckout').
    Esto genera un TypeError que interrumpe el callback, dejando sin registrar el
    listener del ícono .fa-trash-can. En consecuencia, ningún clic en el ícono de
    eliminar tiene efecto sobre el DOM ni sobre localStorage.
    """

    @pytest.mark.xfail(
        reason=(
            "DEFECTO CONOCIDO CP-RF-04-01: scriptCarro.js falla en DOMContentLoaded "
            "al intentar llamar .addEventListener sobre document.getElementById('btnPago') "
            "que retorna null (el template usa id='btnCheckout'). El listener de "
            ".fa-trash-can nunca se registra, por lo que el clic en 'Eliminar' no "
            "modifica el carrito. Veredicto original: FALLIDO."
        ),
        strict=True,
    )
    def test_cp_rf_04_01_eliminar_producto_actualiza_carrito(
        self, driver, app_url, existing_user_credentials, wait, capture_screenshot
    ):
        """
        CP-RF-04-01 — Verificar que el usuario puede eliminar un producto del carrito
        y este se actualiza correctamente.

        Precondiciones:
          - El usuario está autenticado.
          - El carrito contiene al menos un producto.

        Pasos:
          1. Navegar al carrito de compras.
          2. Identificar el producto a eliminar.
          3. Hacer clic en el botón 'Eliminar' (ícono de papelera).
          4. Verificar que el producto ya no aparece en el carrito.

        Resultado esperado:
          El producto desaparece del carrito y del localStorage.

        Veredicto original: FALLIDO — el listener de eliminación nunca se registra.
        Este test está marcado como xfail por el defecto conocido.
        """
        _login(
            driver, wait, app_url,
            existing_user_credentials["username"],
            existing_user_credentials["password"],
        )

        # Inyectar un ítem en el carrito vía localStorage
        items_iniciales = [
            {"id": 1, "title": "Ant-Man (2003)", "price": 6000,
             "img": "/static/img/antman.jpg", "quantity": 1}
        ]
        _inyectar_carrito(driver, app_url, items_iniciales)

        # Navegar al carrito y esperar que scriptCarro.js renderice los ítems
        driver.get(f"{app_url}/carrito/")
        time.sleep(1)
        capture_screenshot("cp_rf_04_01_paso1_carrito_con_item")

        # Verificar que el ítem aparece en la tabla
        filas_antes = driver.find_elements(By.CSS_SELECTOR, "#mostrarCarrito tr")
        assert len(filas_antes) > 0, (
            "CP-RF-04-01: El ítem inyectado no se renderizó en la tabla del carrito."
        )

        # Paso 3: hacer clic en el ícono de eliminar
        icono_eliminar = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".fa-trash-can"))
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", icono_eliminar
        )
        time.sleep(0.3)
        icono_eliminar.click()
        time.sleep(1)
        capture_screenshot("cp_rf_04_01_paso2_tras_eliminar")

        # Resultado esperado: el carrito en localStorage debe estar vacío
        carrito_tras = _leer_carrito(driver)

        # DEFECTO: el clic no tuvo efecto → el ítem sigue en carrito → aserción falla → XFAIL
        assert len(carrito_tras) == 0, (
            "DEFECTO CP-RF-04-01: El producto sigue en el carrito tras hacer clic en "
            "el ícono de eliminar. El listener .fa-trash-can no está registrado."
        )

    @pytest.mark.xfail(
        reason=(
            "DEFECTO CONOCIDO CP-RF-04-02: Mismo defecto que CP-RF-04-01. "
            "El listener de eliminación no se registra en scriptCarro.js. "
            "Al intentar eliminar el único producto, el carrito no queda vacío "
            "ni se muestra el mensaje 'Tu carrito está vacío'. Veredicto original: FALLIDO."
        ),
        strict=True,
    )
    def test_cp_rf_04_02_eliminar_unico_producto_muestra_carrito_vacio(
        self, driver, app_url, existing_user_credentials, wait, capture_screenshot
    ):
        """
        CP-RF-04-02 — Verificar que al eliminar el único producto el carrito
        queda vacío y se muestra un mensaje adecuado.

        Precondiciones:
          - El usuario está autenticado.
          - El carrito contiene únicamente un producto.

        Pasos:
          1. Navegar al carrito de compras.
          2. Hacer clic en 'Eliminar' sobre el único producto.
          3. Verificar que el carrito queda vacío y se muestra el mensaje.

        Resultado esperado:
          El carrito muestra 'Tu carrito está vacío'. La tabla se oculta.

        Veredicto original: FALLIDO — el listener de eliminación no se registra.
        """
        _login(
            driver, wait, app_url,
            existing_user_credentials["username"],
            existing_user_credentials["password"],
        )

        # Inyectar un único ítem
        items_iniciales = [
            {"id": 2, "title": "Spider-Man (2018)", "price": 8500,
             "img": "/static/img/spiderman.jpg", "quantity": 1}
        ]
        _inyectar_carrito(driver, app_url, items_iniciales)

        driver.get(f"{app_url}/carrito/")
        time.sleep(1)
        capture_screenshot("cp_rf_04_02_paso1_carrito_un_item")

        # Verificar que hay exactamente 1 ítem renderizado
        filas = driver.find_elements(By.CSS_SELECTOR, "#mostrarCarrito tr")
        assert len(filas) == 1, (
            f"CP-RF-04-02: Se esperaba 1 fila en la tabla, se encontraron {len(filas)}."
        )

        # Paso 2: eliminar
        icono_eliminar = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".fa-trash-can"))
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", icono_eliminar
        )
        time.sleep(0.3)
        icono_eliminar.click()
        time.sleep(1)
        capture_screenshot("cp_rf_04_02_paso2_tras_eliminar_unico")

        carrito_tras = _leer_carrito(driver)

        # Resultado esperado: carrito vacío
        # DEFECTO: el ítem sigue en localStorage → aserción falla → XFAIL
        assert len(carrito_tras) == 0, (
            "DEFECTO CP-RF-04-02: El único producto sigue en el carrito tras el clic. "
            "El mensaje 'Tu carrito está vacío' no debería estar oculto."
        )

    @pytest.mark.xfail(
        reason=(
            "DEFECTO CONOCIDO CP-RF-04-03: Mismo defecto que CP-RF-04-01 y CP-RF-04-02. "
            "El listener de eliminación no se registra. El total del carrito no se "
            "recalcula tras el intento de eliminar un producto porque el ítem nunca "
            "se retira del localStorage. Veredicto original: FALLIDO."
        ),
        strict=True,
    )
    def test_cp_rf_04_03_total_se_recalcula_al_eliminar_producto(
        self, driver, app_url, existing_user_credentials, wait, capture_screenshot
    ):
        """
        CP-RF-04-03 — Verificar que el total del carrito se recalcula correctamente
        al eliminar uno de varios productos.

        Precondiciones:
          - El usuario está autenticado.
          - El carrito contiene 3 productos distintos con precios conocidos.

        Pasos:
          1. Navegar al carrito de compras.
          2. Registrar el total actual.
          3. Eliminar un producto.
          4. Verificar que el nuevo total = total anterior − precio del ítem eliminado.

        Resultado esperado:
          El total disminuye en exactamente el precio del ítem eliminado.

        Veredicto original: FALLIDO — el listener de eliminación no se registra.
        """
        _login(
            driver, wait, app_url,
            existing_user_credentials["username"],
            existing_user_credentials["password"],
        )

        # Inyectar 3 productos con precios conocidos
        items_iniciales = [
            {"id": 10, "title": "X-Men (1991)",      "price": 5000,
             "img": "/static/img/xmen.jpg",      "quantity": 1},
            {"id": 11, "title": "Hulk (2008)",        "price": 7000,
             "img": "/static/img/hulk.jpg",      "quantity": 1},
            {"id": 12, "title": "Iron Man (2005)",    "price": 9000,
             "img": "/static/img/ironman.jpg",   "quantity": 1},
        ]
        total_esperado_inicial = sum(i["price"] for i in items_iniciales)  # 21000
        precio_a_eliminar = items_iniciales[0]["price"]  # 5000
        total_esperado_tras = total_esperado_inicial - precio_a_eliminar  # 16000

        _inyectar_carrito(driver, app_url, items_iniciales)

        driver.get(f"{app_url}/carrito/")
        time.sleep(1)
        capture_screenshot("cp_rf_04_03_paso1_tres_items")

        # Verificar total inicial en DOM
        total_texto = driver.find_element(By.ID, "totalCarrito").text  # "$21000"
        capture_screenshot("cp_rf_04_03_paso2_total_inicial_registrado")

        # Paso 3: eliminar el primer ítem (ícono con id=10)
        iconos = driver.find_elements(By.CSS_SELECTOR, ".fa-trash-can")
        assert len(iconos) >= 1, (
            "CP-RF-04-03: No se encontraron íconos de eliminar en la tabla."
        )
        primer_icono = iconos[0]
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", primer_icono
        )
        time.sleep(0.3)
        primer_icono.click()
        time.sleep(1)
        capture_screenshot("cp_rf_04_03_paso3_tras_eliminar")

        carrito_tras = _leer_carrito(driver)

        # Resultado esperado: quedan 2 ítems
        # DEFECTO: siguen 3 ítems porque el listener no está registrado → XFAIL
        assert len(carrito_tras) == 2, (
            f"DEFECTO CP-RF-04-03: Se esperaban 2 ítems tras eliminar, "
            f"pero siguen {len(carrito_tras)}. El total no pudo recalcularse."
        )
        total_real = sum(item["price"] * item["quantity"] for item in carrito_tras)
        assert total_real == total_esperado_tras, (
            f"CP-RF-04-03: Total esperado ${total_esperado_tras}, "
            f"total real ${total_real}."
        )
