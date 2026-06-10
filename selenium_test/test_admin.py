"""
Pruebas automatizadas Selenium — Administración y Búsqueda ComicStore.

Cubre los requerimientos funcionales:
  - RF-07: Agregar producto al catálogo (Admin)
  - RF-08: Modificar producto del catálogo (Admin)
  - RF-09: Eliminar producto del catálogo (Admin)
  - RF-10: Búsqueda de productos en el catálogo

Casos de prueba según documento Casos_de_Prueba_ComicStore_Corregido.docx:
  CP-RF-07-01  Admin agrega nuevo producto con datos válidos (APROBADO)
  CP-RF-07-02  Sistema rechaza creación con campos obligatorios vacíos (XFAIL)
  CP-RF-07-03  Usuario estándar no puede acceder al panel de administración (APROBADO)
  CP-RF-08-01  Admin modifica datos de un producto existente (APROBADO)
  CP-RF-08-02  Sistema rechaza modificación con nombre vacío (XFAIL)
  CP-RF-08-03  Sistema rechaza precio negativo al modificar producto (XFAIL)
  CP-RF-09-01  Admin elimina un producto y deja de ser visible en el catálogo (APROBADO)
  CP-RF-09-02  Sistema solicita confirmación antes de eliminar un producto (APROBADO)
  CP-RF-09-03  Usuario estándar no puede eliminar productos (APROBADO)
  CP-RF-10-01  Búsqueda por nombre retorna resultados correctos (APROBADO)
  CP-RF-10-02  Búsqueda sin resultados muestra mensaje adecuado (APROBADO)
  CP-RF-10-03  Búsqueda no distingue mayúsculas y minúsculas (APROBADO)

Selectores reales de la app:
  Panel admin  : /crud/listar/, /crud/crear/, /crud/editar/<id>/, /crud/eliminar/<id>/
  Listar       : table tbody tr, .fa-pen-to-square (editar), .fa-trash-can (eliminar)
  Crear/Editar : #id_title, #id_description, #id_img_path, #id_price,
                 button[type='submit'] (Guardar)
  Búsqueda     : input[name='q'] (navbar), button[type='submit'] junto al input

Notas sobre defectos conocidos:
  - DEFECTO CP-RF-07-02 / CP-RF-08-02: El formulario usa la validación HTML5 nativa
    (atributo required), que solo muestra el error del primer campo vacío mediante
    un tooltip del navegador. El usuario no puede ver todos los errores a la vez.
    El sistema debería mostrar mensajes de error de Django (ul.errorlist) para todos
    los campos.
  - DEFECTO CP-RF-08-03: El campo Precio (IntegerField) no tiene validación de valor
    mínimo (min > 0). El sistema acepta y guarda precios negativos en la base de datos.
"""

import pytest
import django
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


# ============================================================================
# FIXTURE: SUPERUSUARIO ADMIN
# ============================================================================

@pytest.fixture
def superusuario_admin():
    """
    Crea (o reutiliza) el superusuario 'admin' / 'Admin123!' antes del test
    y lo elimina al finalizar.

    Los tests de RF-07, RF-08, RF-09 requieren un superusuario porque las
    vistas /crud/listar/, /crud/crear/, /crud/editar/ y /crud/eliminar/ están
    protegidas con @superuser_required.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comicstore.settings')
    try:
        django.setup()
    except RuntimeError:
        pass

    from django.contrib.auth.models import User

    username = 'admin'
    password = 'Admin123!'
    email = 'admin@comicstore.cl'

    User.objects.filter(username=username).delete()
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
    )
    yield {'username': username, 'password': password, 'user': user}

    User.objects.filter(username=username).delete()


@pytest.fixture
def comic_de_prueba():
    """
    Crea un cómic de prueba en la BD antes del test y lo elimina después.
    Usado en RF-08 y RF-09 para tener siempre un producto disponible.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comicstore.settings')
    try:
        django.setup()
    except RuntimeError:
        pass

    from crud.models import Comic

    comic = Comic.objects.create(
        title='Test Comic Selenium',
        description='Cómic creado automáticamente para pruebas Selenium.',
        img_path='/static/img/test_selenium.jpg',
        price=5000,
    )
    yield comic

    Comic.objects.filter(id=comic.id).delete()


# ============================================================================
# HELPERS
# ============================================================================

def _login_admin(driver, wait, app_url, credentials):
    """Inicia sesión con el superusuario y espera confirmación."""
    driver.get(f"{app_url}/login/")
    wait.until(EC.presence_of_element_located((By.ID, "id_username"))).send_keys(
        credentials["username"]
    )
    campo = driver.find_element(By.ID, "id_password")
    campo.send_keys(credentials["password"])
    campo.send_keys(Keys.RETURN)
    wait.until(EC.presence_of_element_located((By.ID, "dropdownMenuButton")))


def _guardar_formulario(driver):
    """Hace clic en el botón Guardar usando JS para evitar la navbar sticky."""
    boton = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", boton)


# ============================================================================
# RF-07 — AGREGAR PRODUCTO (ADMIN)
# ============================================================================

class TestAgregarProducto:
    """Casos de prueba CP-RF-07-xx: Agregar producto al catálogo."""

    def test_cp_rf_07_01_admin_agrega_producto_con_datos_validos(
        self, driver, app_url, wait, capture_screenshot,
        superusuario_admin
    ):
        """
        CP-RF-07-01 — Verificar que el administrador puede agregar un nuevo
        producto al catálogo con todos los datos requeridos.

        Precondiciones:
          - El administrador está autenticado con rol de administrador.
          - Se tiene acceso al panel de administración.

        Pasos:
          1. Acceder al panel de administración (/crud/listar/).
          2. Hacer clic en 'Crear Comic'.
          3. Completar todos los campos del formulario con datos válidos.
          4. Hacer clic en 'Guardar'.

        Resultado esperado:
          El producto aparece en el listado del catálogo.

        Veredicto original: APROBADO.
        """
        _login_admin(driver, wait, app_url, superusuario_admin)
        driver.get(f"{app_url}/crud/listar/")
        capture_screenshot("cp_rf_07_01_paso1_listar")

        # Clic en "Crear Comic"
        btn_crear = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='crear']"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_crear)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", btn_crear)

        wait.until(EC.presence_of_element_located((By.ID, "id_title")))
        capture_screenshot("cp_rf_07_01_paso2_formulario_crear")

        titulo_nuevo = "Amazing Spider-Man Test RF-07-01"
        driver.find_element(By.ID, "id_title").send_keys(titulo_nuevo)
        driver.find_element(By.ID, "id_description").send_keys("Primera aparición — Test automatizado")
        driver.find_element(By.ID, "id_img_path").send_keys("/static/img/spiderman.jpg")
        driver.find_element(By.ID, "id_price").send_keys("12000")

        _guardar_formulario(driver)
        capture_screenshot("cp_rf_07_01_paso3_resultado")

        # Resultado: redirige a /crud/listar/ y el producto aparece en la tabla
        wait.until(EC.url_contains("/crud/listar/"))
        assert titulo_nuevo in driver.page_source, (
            f"CP-RF-07-01: El producto '{titulo_nuevo}' no aparece en el listado "
            "tras ser creado."
        )

        # Limpieza: eliminar el producto recién creado
        from crud.models import Comic
        Comic.objects.filter(title=titulo_nuevo).delete()

    @pytest.mark.xfail(
        reason=(
            "DEFECTO CONOCIDO CP-RF-07-02: El formulario de creación usa validación "
            "HTML5 nativa (atributo required) que solo muestra el error del primer "
            "campo vacío mediante un tooltip del navegador. Los campos posteriores "
            "no se evalúan hasta que el primero sea corregido. El sistema debería "
            "mostrar mensajes de error de Django (ul.errorlist) para todos los campos "
            "obligatorios a la vez. Veredicto original: FALLIDO."
        ),
        strict=True,
    )
    def test_cp_rf_07_02_sistema_rechaza_creacion_con_campos_vacios(
        self, driver, app_url, wait, capture_screenshot, superusuario_admin
    ):
        """
        CP-RF-07-02 — Verificar que el sistema rechaza la creación de un producto
        con campos obligatorios vacíos.

        Precondiciones:
          - El administrador está autenticado.
          - Se tiene acceso al formulario de agregar producto.

        Pasos:
          1. Acceder al formulario de agregar producto.
          2. Dejar en blanco el campo 'Nombre'.
          3. Hacer clic en 'Guardar'.

        Resultado esperado:
          Mensajes de error Django (ul.errorlist) para todos los campos obligatorios.
          El formulario NO avanza; el usuario permanece en /crud/crear/.

        Veredicto original: FALLIDO — el navegador muestra un único tooltip HTML5
        en el primer campo vacío sin evaluar los campos restantes.
        """
        _login_admin(driver, wait, app_url, superusuario_admin)
        driver.get(f"{app_url}/crud/crear/")
        wait.until(EC.presence_of_element_located((By.ID, "id_title")))
        capture_screenshot("cp_rf_07_02_paso1_formulario_vacio")

        # No se completa ningún campo → clic normal (activa HTML5 required)
        boton = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", boton)
        time.sleep(0.3)
        boton.click()
        time.sleep(0.5)
        capture_screenshot("cp_rf_07_02_paso2_resultado")

        # El sistema DEBERÍA mostrar .errorlist de Django para todos los campos
        errorlist = driver.find_elements(By.CSS_SELECTOR, ".errorlist")

        # DEFECTO: el navegador muestra tooltip nativo (no hay .errorlist) → falla → XFAIL
        assert len(errorlist) > 0, (
            "DEFECTO CP-RF-07-02: No se mostraron mensajes de error de Django. "
            "El navegador usa validación HTML5 nativa (tooltip) en lugar de "
            "mostrar todos los errores juntos."
        )

    def test_cp_rf_07_03_usuario_estandar_no_accede_al_panel_admin(
        self, driver, app_url, wait, capture_screenshot,
        existing_user_credentials
    ):
        """
        CP-RF-07-03 — Verificar que un usuario sin rol de administrador no puede
        acceder al panel de administración.

        Precondiciones:
          - El usuario tiene sesión activa con rol de usuario estándar.

        Pasos:
          1. Digitar directamente en la barra de direcciones la URL del panel
             de administración (/crud/listar/).

        Resultado esperado:
          El sistema redirige al home o muestra acceso denegado.
          El usuario NO puede ver el listado de productos del panel.

        Veredicto original: APROBADO.
        """
        # Iniciar sesión como usuario estándar (no superuser)
        from selenium.webdriver.common.keys import Keys as K
        driver.get(f"{app_url}/login/")
        wait.until(EC.presence_of_element_located((By.ID, "id_username"))).send_keys(
            existing_user_credentials["username"]
        )
        campo = driver.find_element(By.ID, "id_password")
        campo.send_keys(existing_user_credentials["password"])
        campo.send_keys(K.RETURN)
        wait.until(EC.presence_of_element_located((By.ID, "dropdownMenuButton")))

        # Intentar acceder al panel admin directamente
        driver.get(f"{app_url}/crud/listar/")
        capture_screenshot("cp_rf_07_03_intento_acceso_panel")

        # El decorator superuser_required redirige al home (landing:index)
        assert "listar" not in driver.current_url.lower(), (
            "CP-RF-07-03: Un usuario estándar pudo acceder a /crud/listar/ "
            "sin tener permisos de administrador."
        )


# ============================================================================
# RF-08 — MODIFICAR PRODUCTO (ADMIN)
# ============================================================================

class TestModificarProducto:
    """Casos de prueba CP-RF-08-xx: Modificar producto del catálogo."""

    def test_cp_rf_08_01_admin_modifica_producto_existente(
        self, driver, app_url, wait, capture_screenshot,
        superusuario_admin, comic_de_prueba
    ):
        """
        CP-RF-08-01 — Verificar que el administrador puede modificar los datos
        de un producto existente y los cambios se reflejan en el catálogo.

        Precondiciones:
          - El administrador está autenticado.
          - Existe al menos un producto en el catálogo.

        Pasos:
          1. Acceder al panel de administración.
          2. Seleccionar el producto a editar.
          3. Modificar el campo 'Título'.
          4. Hacer clic en 'Guardar'.

        Resultado esperado:
          El título actualizado aparece en el listado del catálogo.

        Veredicto original: APROBADO.
        """
        _login_admin(driver, wait, app_url, superusuario_admin)
        driver.get(f"{app_url}/crud/listar/")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))
        capture_screenshot("cp_rf_08_01_paso1_listar")

        # Clic en el ícono de editar del cómic de prueba
        driver.get(f"{app_url}/crud/editar/{comic_de_prueba.id}/")
        wait.until(EC.presence_of_element_located((By.ID, "id_title")))
        capture_screenshot("cp_rf_08_01_paso2_formulario_editar")

        titulo_actualizado = "Test Comic Selenium — EDITADO"
        campo_titulo = driver.find_element(By.ID, "id_title")
        campo_titulo.clear()
        campo_titulo.send_keys(titulo_actualizado)

        _guardar_formulario(driver)
        capture_screenshot("cp_rf_08_01_paso3_resultado")

        wait.until(EC.url_contains("/crud/listar/"))
        assert titulo_actualizado in driver.page_source, (
            f"CP-RF-08-01: El título actualizado '{titulo_actualizado}' no aparece "
            "en el listado tras guardar los cambios."
        )

    @pytest.mark.xfail(
        reason=(
            "DEFECTO CONOCIDO CP-RF-08-02: Al editar un producto y vaciar el campo "
            "'Nombre', el formulario muestra la validación nativa del navegador "
            "('Completa este campo') en lugar del mensaje específico esperado de "
            "Django ('El título es obligatorio.'). El sistema no muestra mensajes "
            "de error personalizados de Django para campos requeridos vacíos. "
            "Veredicto original: FALLIDO."
        ),
        strict=True,
    )
    def test_cp_rf_08_02_sistema_rechaza_modificacion_con_nombre_vacio(
        self, driver, app_url, wait, capture_screenshot,
        superusuario_admin, comic_de_prueba
    ):
        """
        CP-RF-08-02 — Verificar que el sistema rechaza la modificación de un
        producto dejando el nombre vacío.

        Precondiciones:
          - El administrador está autenticado.
          - Existe al menos un producto para editar.

        Pasos:
          1. Acceder al formulario de edición de un producto.
          2. Borrar el contenido del campo 'Nombre'.
          3. Hacer clic en 'Guardar cambios'.

        Resultado esperado:
          Mensaje de error Django: 'El título es obligatorio.'
          El formulario NO avanza; el usuario permanece en /crud/editar/<id>/.

        Veredicto original: FALLIDO — muestra validación nativa del navegador
        en lugar del mensaje específico de Django.
        """
        _login_admin(driver, wait, app_url, superusuario_admin)
        driver.get(f"{app_url}/crud/editar/{comic_de_prueba.id}/")
        wait.until(EC.presence_of_element_located((By.ID, "id_title")))
        capture_screenshot("cp_rf_08_02_paso1_formulario_editar")

        # Vaciar el campo título
        campo_titulo = driver.find_element(By.ID, "id_title")
        campo_titulo.clear()
        capture_screenshot("cp_rf_08_02_paso2_titulo_vacio")

        # Clic normal (activa validación HTML5 nativa)
        boton = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", boton)
        time.sleep(0.3)
        boton.click()
        time.sleep(0.5)
        capture_screenshot("cp_rf_08_02_paso3_resultado")

        errorlist = driver.find_elements(By.CSS_SELECTOR, ".errorlist")

        # DEFECTO: navegador muestra tooltip nativo, no .errorlist de Django → XFAIL
        assert len(errorlist) > 0, (
            "DEFECTO CP-RF-08-02: No se mostraron mensajes de error de Django. "
            "El sistema usa validación HTML5 nativa en lugar de 'El título es obligatorio.'"
        )

    @pytest.mark.xfail(
        reason=(
            "DEFECTO CONOCIDO CP-RF-08-03: El campo Precio (IntegerField) no tiene "
            "validación de valor mínimo. El sistema acepta y guarda precios negativos "
            "en la base de datos sin mostrar ningún mensaje de error. "
            "Veredicto original: FALLIDO."
        ),
        strict=True,
    )
    def test_cp_rf_08_03_sistema_rechaza_precio_negativo(
        self, driver, app_url, wait, capture_screenshot,
        superusuario_admin, comic_de_prueba
    ):
        """
        CP-RF-08-03 — Verificar que el sistema rechaza un precio con valor
        negativo al modificar un producto.

        Precondiciones:
          - El administrador está autenticado.
          - Existe al menos un producto para editar.

        Pasos:
          1. Acceder al formulario de edición de un producto.
          2. Ingresar un precio negativo en el campo 'Precio'.
          3. Hacer clic en 'Guardar cambios'.

        Resultado esperado:
          Mensaje de error: 'El precio debe ser mayor a cero.'
          El formulario NO avanza.

        Veredicto original: FALLIDO — el sistema guarda el precio negativo sin error.
        """
        _login_admin(driver, wait, app_url, superusuario_admin)
        driver.get(f"{app_url}/crud/editar/{comic_de_prueba.id}/")
        wait.until(EC.presence_of_element_located((By.ID, "id_price")))
        capture_screenshot("cp_rf_08_03_paso1_formulario_editar")

        # Ingresar precio negativo
        campo_precio = driver.find_element(By.ID, "id_price")
        campo_precio.clear()
        campo_precio.send_keys("-500")
        capture_screenshot("cp_rf_08_03_paso2_precio_negativo")

        _guardar_formulario(driver)
        time.sleep(0.5)
        capture_screenshot("cp_rf_08_03_paso3_resultado")

        # El sistema DEBERÍA rechazar el precio negativo
        # DEFECTO: guarda el precio y redirige a /crud/listar/ → la URL no es editar → XFAIL
        assert "editar" in driver.current_url.lower(), (
            "DEFECTO CP-RF-08-03: El sistema aceptó un precio negativo (-500) "
            "y redirigió fuera del formulario de edición."
        )


# ============================================================================
# RF-09 — ELIMINAR PRODUCTO (ADMIN)
# ============================================================================

class TestEliminarProducto:
    """Casos de prueba CP-RF-09-xx: Eliminar producto del catálogo."""

    def test_cp_rf_09_01_admin_elimina_producto_y_desaparece_del_catalogo(
        self, driver, app_url, wait, capture_screenshot,
        superusuario_admin, comic_de_prueba
    ):
        """
        CP-RF-09-01 — Verificar que el administrador puede eliminar un producto
        y este deja de ser visible en el catálogo.

        Precondiciones:
          - El administrador está autenticado.
          - Existe al menos un producto en el catálogo.

        Pasos:
          1. Acceder al panel de administración.
          2. Seleccionar el producto a eliminar.
          3. Hacer clic en el ícono de eliminar y confirmar.
          4. Verificar que el producto ya no aparece en el listado.

        Resultado esperado:
          El producto desaparece de /crud/listar/ y del catálogo público.

        Veredicto original: APROBADO.
        """
        _login_admin(driver, wait, app_url, superusuario_admin)
        driver.get(f"{app_url}/crud/listar/")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))

        titulo = comic_de_prueba.title
        comic_id = comic_de_prueba.id
        capture_screenshot("cp_rf_09_01_paso1_listar_con_producto")

        # Navegar directamente a la URL de eliminación (bypass del confirm JS)
        driver.get(f"{app_url}/crud/eliminar/{comic_id}/")
        capture_screenshot("cp_rf_09_01_paso2_producto_eliminado")

        # Resultado: redirige a /crud/listar/ y el producto no aparece
        wait.until(EC.url_contains("/crud/listar/"))
        assert titulo not in driver.page_source, (
            f"CP-RF-09-01: El producto '{titulo}' sigue apareciendo en el listado "
            "después de ser eliminado."
        )

    def test_cp_rf_09_02_sistema_solicita_confirmacion_antes_de_eliminar(
        self, driver, app_url, wait, capture_screenshot,
        superusuario_admin, comic_de_prueba
    ):
        """
        CP-RF-09-02 — Verificar que el sistema solicita confirmación antes de
        eliminar un producto.

        Precondiciones:
          - El administrador está autenticado.
          - Existe al menos un producto en el catálogo.

        Pasos:
          1. Acceder al panel de administración.
          2. Hacer clic en 'Eliminar' sobre un producto.
          3. Verificar que aparece el diálogo de confirmación.

        Resultado esperado:
          Se muestra un diálogo de confirmación con el mensaje
          '¿Estás seguro de que quieres eliminar este cómic?'.

        Veredicto original: APROBADO.
        """
        _login_admin(driver, wait, app_url, superusuario_admin)
        driver.get(f"{app_url}/crud/listar/")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))
        capture_screenshot("cp_rf_09_02_paso1_listar")

        # Hacer clic en el ícono de eliminar (dispara el confirm de JS)
        icono_eliminar = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".fa-trash-can"))
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", icono_eliminar
        )
        time.sleep(0.3)
        icono_eliminar.click()

        # El onclick del link dispara window.confirm → aparece alerta del navegador
        try:
            alerta = driver.switch_to.alert
            texto_alerta = alerta.text
            capture_screenshot("cp_rf_09_02_paso2_dialogo_confirmacion")

            # Cancelar para no eliminar el producto
            alerta.dismiss()

            assert "eliminar" in texto_alerta.lower(), (
                f"CP-RF-09-02: El diálogo no contiene la palabra 'eliminar'. "
                f"Texto: '{texto_alerta}'"
            )
        except Exception:
            # Si no aparece alerta, el navegador no mostró confirmación
            raise AssertionError(
                "CP-RF-09-02: No apareció el diálogo de confirmación al hacer "
                "clic en 'Eliminar'."
            )

    def test_cp_rf_09_03_usuario_estandar_no_puede_eliminar_productos(
        self, driver, app_url, wait, capture_screenshot,
        existing_user_credentials, comic_de_prueba
    ):
        """
        CP-RF-09-03 — Verificar que un usuario sin rol de administrador no puede
        eliminar productos.

        Precondiciones:
          - El usuario tiene sesión con rol estándar.

        Pasos:
          1. Intentar acceder directamente a la URL de eliminación de un producto.

        Resultado esperado:
          El sistema redirige al home o muestra acceso denegado.
          El producto sigue existiendo en la BD.

        Veredicto original: APROBADO.
        """
        from selenium.webdriver.common.keys import Keys as K

        # Login como usuario estándar
        driver.get(f"{app_url}/login/")
        wait.until(EC.presence_of_element_located((By.ID, "id_username"))).send_keys(
            existing_user_credentials["username"]
        )
        campo = driver.find_element(By.ID, "id_password")
        campo.send_keys(existing_user_credentials["password"])
        campo.send_keys(K.RETURN)
        wait.until(EC.presence_of_element_located((By.ID, "dropdownMenuButton")))

        # Intentar acceder directo a la URL de eliminar
        driver.get(f"{app_url}/crud/eliminar/{comic_de_prueba.id}/")
        capture_screenshot("cp_rf_09_03_intento_eliminar")

        # El decorator superuser_required redirige al home
        assert "eliminar" not in driver.current_url.lower(), (
            "CP-RF-09-03: Un usuario estándar pudo acceder a la URL de eliminación "
            "sin tener permisos de administrador."
        )

        # Verificar que el producto sigue en la BD
        from crud.models import Comic
        assert Comic.objects.filter(id=comic_de_prueba.id).exists(), (
            "CP-RF-09-03: El producto fue eliminado pese a que el usuario no "
            "tenía permisos de administrador."
        )


# ============================================================================
# RF-10 — BÚSQUEDA EN EL CATÁLOGO
# ============================================================================

class TestBusquedaCatalogo:
    """Casos de prueba CP-RF-10-xx: Búsqueda de productos en el catálogo."""

    def test_cp_rf_10_01_busqueda_por_nombre_retorna_resultados_correctos(
        self, driver, app_url, wait, capture_screenshot
    ):
        """
        CP-RF-10-01 — Verificar que el usuario puede buscar productos por nombre
        y los resultados son correctos.

        Precondiciones:
          - El sistema está disponible.
          - Existen productos en el catálogo cuyo nombre contiene 'spider'.

        Pasos:
          1. Ingresar el término 'spider' en el campo de búsqueda.
          2. Hacer clic en el botón de búsqueda.
          3. Verificar que los resultados contienen 'spider'.

        Resultado esperado:
          Los resultados de búsqueda muestran productos con 'spider' en el título.

        Veredicto original: APROBADO.
        """
        driver.get(f"{app_url}/")
        capture_screenshot("cp_rf_10_01_paso1_landing")

        campo_busqueda = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='q']"))
        )
        campo_busqueda.clear()
        campo_busqueda.send_keys("spider")
        campo_busqueda.send_keys(Keys.RETURN)

        wait.until(EC.presence_of_element_located((By.ID, "comics")))
        capture_screenshot("cp_rf_10_01_paso2_resultados")

        assert "spider" in driver.current_url.lower() or \
               "Resultados para" in driver.page_source, (
            "CP-RF-10-01: La búsqueda no redirigió ni mostró el encabezado de resultados."
        )

        tarjetas = driver.find_elements(By.CSS_SELECTOR, "#comics .card")
        if len(tarjetas) > 0:
            # Si hay resultados, al menos uno debe contener 'spider' en el título
            titulos = [t.find_element(By.CSS_SELECTOR, ".card-title").text.lower()
                       for t in tarjetas
                       if t.find_elements(By.CSS_SELECTOR, ".card-title")]
            assert any("spider" in t for t in titulos), (
                "CP-RF-10-01: Los resultados no contienen productos con 'spider' en el título."
            )

    def test_cp_rf_10_02_busqueda_sin_resultados_muestra_mensaje_adecuado(
        self, driver, app_url, wait, capture_screenshot
    ):
        """
        CP-RF-10-02 — Verificar que el sistema muestra un mensaje adecuado
        cuando la búsqueda no retorna resultados.

        Precondiciones:
          - La página está disponible.
          - No existe ningún producto con el nombre 'asdada' en el catálogo.

        Pasos:
          1. Ingresar 'asdada' en el campo de búsqueda.
          2. Hacer clic en el botón de búsqueda.
          3. Verificar que se muestra el mensaje de sin resultados.

        Resultado esperado:
          Mensaje: 'No se encontraron resultados para "asdada".'

        Veredicto original: APROBADO.
        """
        driver.get(f"{app_url}/")

        campo_busqueda = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='q']"))
        )
        campo_busqueda.clear()
        campo_busqueda.send_keys("asdada_xyz_inexistente")
        campo_busqueda.send_keys(Keys.RETURN)

        wait.until(EC.presence_of_element_located((By.ID, "comics")))
        capture_screenshot("cp_rf_10_02_resultados_vacios")

        assert "No se encontraron resultados" in driver.page_source, (
            "CP-RF-10-02: No se mostró el mensaje 'No se encontraron resultados' "
            "para una búsqueda sin coincidencias."
        )

    def test_cp_rf_10_03_busqueda_no_distingue_mayusculas_minusculas(
        self, driver, app_url, wait, capture_screenshot
    ):
        """
        CP-RF-10-03 — Verificar que la búsqueda no distingue entre mayúsculas
        y minúsculas.

        Precondiciones:
          - Existen productos con 'Ant-Man' en el catálogo.

        Pasos:
          1. Buscar con 'ant' (minúsculas).
          2. Buscar con 'ANT' (mayúsculas).
          3. Verificar que ambas búsquedas retornan los mismos resultados.

        Resultado esperado:
          Ambas búsquedas devuelven la misma cantidad de resultados.

        Veredicto original: APROBADO.
        """
        def _buscar(termino):
            driver.get(f"{app_url}/")
            campo = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='q']"))
            )
            campo.clear()
            campo.send_keys(termino)
            campo.send_keys(Keys.RETURN)
            wait.until(EC.presence_of_element_located((By.ID, "comics")))
            return driver.find_elements(By.CSS_SELECTOR, "#comics .card")

        tarjetas_min = _buscar("ant")
        capture_screenshot("cp_rf_10_03_paso1_busqueda_minusculas")

        tarjetas_may = _buscar("ANT")
        capture_screenshot("cp_rf_10_03_paso2_busqueda_mayusculas")

        assert len(tarjetas_min) == len(tarjetas_may), (
            f"CP-RF-10-03: La búsqueda distingue mayúsculas/minúsculas. "
            f"'ant' retornó {len(tarjetas_min)} resultado(s), "
            f"'ANT' retornó {len(tarjetas_may)} resultado(s)."
        )
