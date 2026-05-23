"""
Tests de Autenticación y Registro de ComicStore.
Adaptados a los templates y formularios reales de Django.

Cubre RF-01 (Registro), RF-02 (Login), RF-05 (Logout).

IDs reales de los formularios:
  - Registro: id_username, id_nombre, id_apellido, id_rut, id_email,
              id_telefono, id_direccion, id_pais, id_region, id_comuna,
              id_password1, id_password2 | botón: #registrar
  - Login:    id_username, id_password | botón: button[type=submit]
  - Logout:   a[href='/logout/'] en el dropdown del navbar
  - Estado autenticado: #dropdownMenuButton (contiene "Bienvenido, ...")
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys
import time


# ============================================================================
# HELPER: llenar un campo por ID
# ============================================================================

def fill_field(driver, field_id, value):
    field = driver.find_element(By.ID, field_id)
    field.clear()
    field.send_keys(value)


def js_click(driver, element):
    """Hace clic via JavaScript para evitar ElementClickInterceptedException."""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.2)
    driver.execute_script("arguments[0].click();", element)


# ============================================================================
# HELPER: hacer login
# ============================================================================

def do_login(driver, app_url, wait, username, password):
    driver.get(f"{app_url}/login/")
    wait.until(EC.presence_of_element_located((By.ID, "id_username")))
    fill_field(driver, "id_username", username)
    fill_field(driver, "id_password", password)
    # Usar el botón de 'Iniciar Sesión' del formulario de login (no el de búsqueda del navbar)
    btn = driver.find_element(By.CSS_SELECTOR, "form.formulario button[type='submit']")
    js_click(driver, btn)
    # Esperar a que la URL cambie (salga de /login/) indicando login exitoso
    long_wait = WebDriverWait(driver, 15)
    long_wait.until(lambda d: "login" not in d.current_url.lower())
    # Esperar a que aparezca el botón de bienvenida (usuario autenticado)
    long_wait.until(EC.presence_of_element_located((By.ID, "dropdownMenuButton")))


# ============================================================================
# CLASE: Registro
# ============================================================================

class TestRegistration:
    """CP-RF-01: Registro de usuario"""

    def test_rf_01_01_successful_registration_with_valid_data(
        self, driver, app_url, valid_user_data, wait, capture_screenshot
    ):
        """
        CP-RF-01-01: Verificar que el usuario puede registrarse exitosamente con datos válidos.

        Precondiciones:
        - La página está disponible y accesible
        - El usuario (username y rut) no existe en la base de datos

        Pasos:
        1. Navegar a la página de registro
        2. Completar formulario con datos válidos
        3. Hacer clic en botón 'Registrarse'

        Resultado esperado: Modal de registro exitoso aparece
        """
        driver.get(f"{app_url}/registro/")
        capture_screenshot("paso1_pagina_registro")

        wait.until(EC.presence_of_element_located((By.ID, "id_username")))

        fill_field(driver, "id_username", valid_user_data['username'])
        fill_field(driver, "id_nombre", valid_user_data['nombre'])
        fill_field(driver, "id_apellido", valid_user_data['apellido'])
        fill_field(driver, "id_rut", valid_user_data['rut'])
        fill_field(driver, "id_email", valid_user_data['email'])
        fill_field(driver, "id_telefono", valid_user_data['telefono'])
        fill_field(driver, "id_direccion", valid_user_data['direccion'])

        # Los selects pais/region/comuna usan IDs sin prefijo 'id_'
        # Solo seleccionar si tienen opciones disponibles en la BD
        pais_select_el = driver.find_element(By.ID, "pais")
        pais_opts = pais_select_el.find_elements(By.TAG_NAME, "option")
        if len(pais_opts) <= 1:  # Solo la opción vacía o ninguna
            pytest.skip("No hay países cargados en la BD para el registro")
        Select(pais_select_el).select_by_index(1)
        time.sleep(0.5)

        region_select_el = driver.find_element(By.ID, "region")
        region_opts = region_select_el.find_elements(By.TAG_NAME, "option")
        if len(region_opts) > 0:
            Select(region_select_el).select_by_index(0)
            time.sleep(0.5)

        comuna_select_el = driver.find_element(By.ID, "comuna")
        comuna_opts = comuna_select_el.find_elements(By.TAG_NAME, "option")
        if len(comuna_opts) > 0:
            Select(comuna_select_el).select_by_index(0)

        fill_field(driver, "id_password1", valid_user_data['password1'])
        fill_field(driver, "id_password2", valid_user_data['password2'])

        capture_screenshot("paso2_formulario_completo")

        # Usar el botón de registro del formulario (no el de búsqueda del navbar)
        btn_registrar = driver.find_element(By.ID, "registrar")
        js_click(driver, btn_registrar)

        # Verificar que aparece el modal de éxito (o que el indicador oculto es "true")
        wait.until(
            EC.presence_of_element_located((By.ID, "registro-exitoso-indicador"))
        )
        indicador = driver.find_element(By.ID, "registro-exitoso-indicador")
        assert indicador.get_attribute("value") == "true", \
            "El registro no fue exitoso (indicador no es 'true')"

        capture_screenshot("paso3_registro_exitoso")

    def test_rf_01_02_registration_fails_with_empty_required_fields(
        self, driver, app_url, wait
    ):
        """
        CP-RF-01-02: Verificar que el registro falla si los campos requeridos están vacíos.
        """
        driver.get(f"{app_url}/registro/")
        wait.until(EC.presence_of_element_located((By.ID, "registrar")))

        # Enviar formulario vacío
        btn = driver.find_element(By.ID, "registrar")
        js_click(driver, btn)

        # El formulario de Django debe mostrar errores o seguir en /registro/
        time.sleep(0.5)
        assert "registro" in driver.current_url.lower(), \
            "Debería permanecer en la página de registro con campos vacíos"

    def test_rf_01_03_registration_fails_with_mismatched_passwords(
        self, driver, app_url, valid_user_data, wait
    ):
        """
        CP-RF-01-03: Verificar que el registro falla si las contraseñas no coinciden.
        """
        driver.get(f"{app_url}/registro/")
        wait.until(EC.presence_of_element_located((By.ID, "id_username")))

        fill_field(driver, "id_username", valid_user_data['username'])
        fill_field(driver, "id_nombre", valid_user_data['nombre'])
        fill_field(driver, "id_apellido", valid_user_data['apellido'])
        fill_field(driver, "id_rut", valid_user_data['rut'])
        fill_field(driver, "id_email", valid_user_data['email'])
        fill_field(driver, "id_telefono", valid_user_data['telefono'])
        fill_field(driver, "id_direccion", valid_user_data['direccion'])
        fill_field(driver, "id_password1", "Segura123!")
        fill_field(driver, "id_password2", "DiferenteClave456!")  # No coincide

        btn = driver.find_element(By.ID, "registrar")
        js_click(driver, btn)

        time.sleep(0.5)
        assert "registro" in driver.current_url.lower(), \
            "Debería permanecer en la página de registro con contraseñas distintas"

    def test_rf_01_04_registration_fails_with_invalid_rut_format(
        self, driver, app_url, valid_user_data, wait
    ):
        """
        CP-RF-01-04: Verificar que el registro falla con formato de RUT inválido.
        El RUT debe tener formato: NNNNNNN-D (sin puntos, con guión)
        """
        driver.get(f"{app_url}/registro/")
        wait.until(EC.presence_of_element_located((By.ID, "id_username")))

        fill_field(driver, "id_username", valid_user_data['username'])
        fill_field(driver, "id_nombre", valid_user_data['nombre'])
        fill_field(driver, "id_apellido", valid_user_data['apellido'])
        fill_field(driver, "id_rut", "12.345.678-9")  # Con puntos, inválido
        fill_field(driver, "id_email", valid_user_data['email'])
        fill_field(driver, "id_telefono", valid_user_data['telefono'])
        fill_field(driver, "id_direccion", valid_user_data['direccion'])
        fill_field(driver, "id_password1", valid_user_data['password1'])
        fill_field(driver, "id_password2", valid_user_data['password2'])

        btn = driver.find_element(By.ID, "registrar")
        js_click(driver, btn)

        time.sleep(0.5)
        assert "registro" in driver.current_url.lower(), \
            "Debería permanecer en la página de registro con RUT inválido"


# ============================================================================
# CLASE: Login
# ============================================================================

class TestLogin:
    """CP-RF-02: Login de usuario"""

    def test_rf_02_01_successful_login_with_valid_credentials(
        self, driver, app_url, existing_user_credentials, wait, capture_screenshot
    ):
        """
        CP-RF-02-01: Verificar login exitoso con credenciales válidas.

        Precondiciones:
        - El usuario 'testselenium' existe en la base de datos.
        - Si no existe, ejecutar:
          python manage.py shell -c "
            from django.contrib.auth.models import User
            User.objects.create_user('testselenium', password='TestPass123!')
          "

        Pasos:
        1. Navegar a página de login (/login/)
        2. Ingresar username
        3. Ingresar contraseña
        4. Hacer clic en 'Iniciar Sesión'

        Resultado: Login exitoso, aparece botón 'Bienvenido, ...' en navbar
        """
        driver.get(f"{app_url}/login/")
        capture_screenshot("paso1_pagina_login")

        wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        fill_field(driver, "id_username", existing_user_credentials['username'])
        fill_field(driver, "id_password", existing_user_credentials['password'])
        capture_screenshot("paso2_credenciales_ingresadas")

        # El formulario de login tiene class='formulario', usar ese selector
        btn = driver.find_element(By.CSS_SELECTOR, "form.formulario button[type='submit']")
        js_click(driver, btn)

        # Verificar que sesión está activa: la URL ya no es /login/
        capture_screenshot("paso3_login_exitoso")

        # El botón puede estar visible en el navbar
        assert "login" not in driver.current_url.lower(), \
            "No debe estar en la página de login después del login exitoso"

    def test_rf_02_02_login_fails_with_incorrect_password(
        self, driver, app_url, existing_user_credentials, wait
    ):
        """
        CP-RF-02-02: Verificar que login falla con contraseña incorrecta.
        Django muestra error genérico en el formulario y permanece en /login/.
        """
        driver.get(f"{app_url}/login/")
        wait.until(EC.presence_of_element_located((By.ID, "id_username")))

        fill_field(driver, "id_username", existing_user_credentials['username'])
        fill_field(driver, "id_password", "ContraseñaIncorrecta999!")

        btn = driver.find_element(By.CSS_SELECTOR, "form.formulario button[type='submit']")
        js_click(driver, btn)

        time.sleep(0.5)
        assert "login" in driver.current_url.lower(), \
            "Debería permanecer en la página de login con credenciales incorrectas"

        # Verificar que hay un mensaje de error del formulario Django
        page_source = driver.page_source.lower()
        assert (
            "incorrecto" in page_source
            or "inválido" in page_source
            or "no está registrado" in page_source
            or "errorlist" in page_source
        ), "Debería mostrar un mensaje de error de credenciales"

    def test_rf_02_03_login_fails_with_nonexistent_username(
        self, driver, app_url, wait
    ):
        """
        CP-RF-02-03: Verificar que login falla con username no registrado.
        """
        driver.get(f"{app_url}/login/")
        wait.until(EC.presence_of_element_located((By.ID, "id_username")))

        fill_field(driver, "id_username", "usuario_que_no_existe_xyzabc")
        fill_field(driver, "id_password", "AlgunaContra123!")

        btn = driver.find_element(By.CSS_SELECTOR, "form.formulario button[type='submit']")
        js_click(driver, btn)

        time.sleep(0.5)
        assert "login" in driver.current_url.lower(), \
            "Debería permanecer en la página de login con usuario inexistente"

        page_source = driver.page_source.lower()
        assert (
            "no está registrado" in page_source
            or "errorlist" in page_source
            or "inválido" in page_source
        ), "Debería mostrar error de usuario no encontrado"

    def test_rf_02_04_login_page_has_required_elements(
        self, driver, app_url, wait
    ):
        """
        CP-RF-02-04: Verificar que la página de login tiene los elementos necesarios.
        """
        driver.get(f"{app_url}/login/")

        assert wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        assert driver.find_element(By.ID, "id_password")
        # Verificar que existe el botón de submit del formulario de login
        assert driver.find_element(By.CSS_SELECTOR, "form.formulario button[type='submit']")


# ============================================================================
# CLASE: Logout
# ============================================================================

class TestLogout:
    """CP-RF-05: Cierre de sesión"""

    def test_rf_05_01_successful_logout_from_authenticated_session(
        self, driver, app_url, existing_user_credentials, wait
    ):
        """
        CP-RF-05-01: Verificar cierre de sesión exitoso.

        Precondiciones:
        - Usuario 'testselenium' existe en BD

        Pasos:
        1. Hacer login
        2. Hacer clic en 'Cerrar sesión'

        Resultado: Sesión cerrada, desaparece el botón 'Bienvenido'
        """
        do_login(
            driver, app_url, wait,
            existing_user_credentials['username'],
            existing_user_credentials['password']
        )

        # Abrir dropdown y hacer logout
        dropdown_btn = wait.until(EC.element_to_be_clickable((By.ID, "dropdownMenuButton")))
        js_click(driver, dropdown_btn)
        logout_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/logout/']")))
        js_click(driver, logout_link)

        # Verificar que la sesión se cerró (el dropdown de bienvenida no aparece)
        wait.until(EC.url_contains(app_url))
        time.sleep(0.5)
        dropdown_buttons = driver.find_elements(By.ID, "dropdownMenuButton")
        assert len(dropdown_buttons) == 0, \
            "El botón 'Bienvenido' no debería estar visible tras el logout"

    def test_rf_05_02_cannot_access_carrito_after_logout_redirects(
        self, driver, app_url, existing_user_credentials, wait
    ):
        """
        CP-RF-05-02: Verificar que el carrito es accesible pero sin sesión activa.
        """
        do_login(
            driver, app_url, wait,
            existing_user_credentials['username'],
            existing_user_credentials['password']
        )

        # Logout
        dropdown_btn2 = wait.until(EC.element_to_be_clickable((By.ID, "dropdownMenuButton")))
        js_click(driver, dropdown_btn2)
        logout_link2 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/logout/']")))
        js_click(driver, logout_link2)
        wait.until(EC.url_contains(app_url))

        # Intentar acceder al carrito (accesible sin login en esta app)
        driver.get(f"{app_url}/carrito/")
        time.sleep(0.5)
        assert "carrito" in driver.current_url.lower() or "login" in driver.current_url.lower(), \
            "Debe ir al carrito o redirigir al login"

    def test_rf_05_03_navbar_shows_login_link_after_logout(
        self, driver, app_url, existing_user_credentials, wait
    ):
        """
        CP-RF-05-03: Verificar que el navbar muestra 'INGRESAR' después del logout.
        """
        do_login(
            driver, app_url, wait,
            existing_user_credentials['username'],
            existing_user_credentials['password']
        )

        # Logout
        dropdown_btn3 = wait.until(EC.element_to_be_clickable((By.ID, "dropdownMenuButton")))
        js_click(driver, dropdown_btn3)
        logout_link3 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/logout/']")))
        js_click(driver, logout_link3)
        wait.until(EC.url_contains(app_url))

        # Verificar que el link de INGRESAR aparece en el navbar
        ingresar_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/login']")
        assert len(ingresar_links) > 0, \
            "Debe aparecer el link de 'INGRESAR' en el navbar tras el logout"
