"""
Tests de Autenticación y Registro de ComicStore.
Cubre RF-01 (Registro), RF-02 (Login), RF-05 (Logout).
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


class TestRegistration:
    """CP-RF-01: Registro de usuario"""

    def test_rf_01_01_successful_registration_with_valid_data(self, driver, app_url, valid_user_data, wait, capture_screenshot):
        """
        CP-RF-01-01: Verificar que el usuario puede registrarse exitosamente con datos válidos.

        Precondiciones:
        - La página está disponible y accesible
        - El usuario no tiene cuenta registrada con el correo a utilizar

        Pasos:
        1. Navegar a la página de registro
        2. Completar formulario con datos válidos
        3. Hacer clic en botón 'Registrarse'

        Resultado esperado: Registro exitoso, redirige a home o página de bienvenida
        """
        driver.get(f"{app_url}/registro")
        capture_screenshot("paso1_pagina_registro")

        # Llenar formulario de registro
        wait.until(EC.presence_of_element_located((By.ID, "nombre"))).send_keys(valid_user_data['nombre'])
        driver.find_element(By.ID, "email").send_keys(valid_user_data['email'])
        driver.find_element(By.ID, "rut").send_keys(valid_user_data['rut'])
        driver.find_element(By.ID, "contraseña").send_keys(valid_user_data['contraseña'])
        driver.find_element(By.ID, "confirmar_contraseña").send_keys(valid_user_data['confirmar_contraseña'])
        capture_screenshot("paso2_formulario_completo")

        # Hacer clic en botón Registrarse
        driver.find_element(By.ID, "btn-registrarse").click()

        # Verificar redirección exitosa
        wait.until(EC.url_contains(f"{app_url}/"))
        capture_screenshot("paso3_registro_exitoso")

        assert driver.current_url == f"{app_url}/" or "bienvenida" in driver.current_url.lower()

        # Verificar mensaje de bienvenida o usuario logueado
        assert wait.until(EC.presence_of_element_located((By.CLASS_NAME, "usuario-logueado")))

    @pytest.mark.parametrize("email", [
        "user@example.com",
        "first.last@domain.co.uk",
        "user+tag@example.com",
    ])
    def test_rf_01_02_registration_with_valid_email_formats(self, driver, app_url, valid_user_data, wait, email):
        """
        CP-RF-01-02: Validar que se aceptan diferentes formatos válidos de email.

        Escenarios:
        - Email simple: user@example.com
        - Email con punto: first.last@domain.co.uk
        - Email con etiqueta: user+tag@example.com
        """
        driver.get(f"{app_url}/registro")

        valid_user_data['email'] = email

        # Llenar formulario
        wait.until(EC.presence_of_element_located((By.ID, "nombre"))).send_keys(valid_user_data['nombre'])
        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "rut").send_keys(valid_user_data['rut'])
        driver.find_element(By.ID, "contraseña").send_keys(valid_user_data['contraseña'])
        driver.find_element(By.ID, "confirmar_contraseña").send_keys(valid_user_data['contraseña'])

        # Enviar formulario
        driver.find_element(By.ID, "btn-registrarse").click()

        # Verificar que la validación pasó (no hay error de email)
        wait.until(EC.url_contains(f"{app_url}/"))
        assert "registro" not in driver.current_url.lower()

    @pytest.mark.parametrize("invalid_email,descripcion", [
        ("", "Email vacío"),
        ("invalid-email", "Sin símbolo @"),
        ("@example.com", "Sin parte local"),
        ("usuario@", "Sin dominio"),
    ])
    def test_rf_01_03_registration_fails_with_invalid_email(self, driver, app_url, valid_user_data, wait, invalid_email, descripcion):
        """
        CP-RF-01-03: Verificar que el registro falla con emails inválidos.

        Casos:
        - Email vacío
        - Email sin @
        - Email sin parte local
        - Email sin dominio
        """
        driver.get(f"{app_url}/registro")

        # Llenar formulario con email inválido
        wait.until(EC.presence_of_element_located((By.ID, "nombre"))).send_keys(valid_user_data['nombre'])
        email_field = driver.find_element(By.ID, "email")
        email_field.send_keys(invalid_email)
        driver.find_element(By.ID, "rut").send_keys(valid_user_data['rut'])
        driver.find_element(By.ID, "contraseña").send_keys(valid_user_data['contraseña'])
        driver.find_element(By.ID, "confirmar_contraseña").send_keys(valid_user_data['contraseña'])

        # Intentar enviar
        driver.find_element(By.ID, "btn-registrarse").click()

        # Verificar que no se registró (sigue en la página de registro)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error-email")))
        assert "registro" in driver.current_url.lower()


class TestLogin:
    """CP-RF-02: Login de usuario"""

    def test_rf_02_01_successful_login_with_valid_credentials(self, driver, app_url, existing_user_credentials, wait, capture_screenshot):
        """
        CP-RF-02-01: Verificar login exitoso con credenciales válidas.

        Precondiciones:
        - El usuario tiene una cuenta registrada
        - Las credenciales son correctas

        Pasos:
        1. Navegar a página de login
        2. Ingresar email
        3. Ingresar contraseña
        4. Hacer clic en 'Ingresar'

        Resultado: Login exitoso, sesión iniciada
        """
        driver.get(f"{app_url}/login")
        capture_screenshot("paso1_pagina_login")

        # Llenar credenciales
        wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(existing_user_credentials['email'])
        driver.find_element(By.ID, "contraseña").send_keys(existing_user_credentials['contraseña'])
        capture_screenshot("paso2_credenciales_ingresadas")

        # Hacer clic en botón Ingresar
        driver.find_element(By.ID, "btn-ingresar").click()

        # Verificar que sesión está activa
        wait.until(EC.url_contains(f"{app_url}/"))
        capture_screenshot("paso3_login_exitoso")

        assert wait.until(EC.presence_of_element_located((By.CLASS_NAME, "usuario-logueado")))
        assert existing_user_credentials['email'] in driver.page_source

    def test_rf_02_02_login_fails_with_incorrect_password(self, driver, app_url, existing_user_credentials, wait):
        """
        CP-RF-02-02: Verificar que login falla con contraseña incorrecta.
        """
        driver.get(f"{app_url}/login")

        # Ingresar email correcto pero contraseña incorrecta
        wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(existing_user_credentials['email'])
        driver.find_element(By.ID, "contraseña").send_keys("ContraseñaIncorrecta123!")

        driver.find_element(By.ID, "btn-ingresar").click()

        # Verificar mensaje de error
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error-credenciales")))
        assert "login" in driver.current_url.lower()

    def test_rf_02_03_login_fails_with_nonexistent_email(self, driver, app_url, wait):
        """
        CP-RF-02-03: Verificar que login falla con email no registrado.
        """
        driver.get(f"{app_url}/login")

        # Ingresar email que no existe
        wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys("noeexiste@example.com")
        driver.find_element(By.ID, "contraseña").send_keys("AlgunaContraseña123!")

        driver.find_element(By.ID, "btn-ingresar").click()

        # Verificar mensaje de error
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error-usuario-no-encontrado")))
        assert "login" in driver.current_url.lower()


class TestLogout:
    """CP-RF-05: Cierre de sesión"""

    def test_rf_05_01_successful_logout_from_authenticated_session(self, driver, app_url, existing_user_credentials, wait):
        """
        CP-RF-05-01: Verificar cierre de sesión exitoso.

        Precondiciones:
        - Usuario está logueado

        Pasos:
        1. Navegar a la página
        2. Hacer clic en 'Cerrar Sesión'

        Resultado: Sesión cerrada, redirige a home sin autenticación
        """
        # Primero hacer login
        driver.get(f"{app_url}/login")
        wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(existing_user_credentials['email'])
        driver.find_element(By.ID, "contraseña").send_keys(existing_user_credentials['contraseña'])
        driver.find_element(By.ID, "btn-ingresar").click()

        # Esperar a que se inicie sesión
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "usuario-logueado")))

        # Hacer click en cerrar sesión
        driver.find_element(By.ID, "btn-cerrar-sesion").click()

        # Verificar que la sesión se cerró
        wait.until(EC.url_contains(f"{app_url}/"))
        assert not driver.find_elements(By.CLASS_NAME, "usuario-logueado")

    def test_rf_05_02_logout_clears_user_session_data(self, driver, app_url, existing_user_credentials, wait):
        """
        CP-RF-05-02: Verificar que logout limpia datos de sesión.
        """
        # Login
        driver.get(f"{app_url}/login")
        wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(existing_user_credentials['email'])
        driver.find_element(By.ID, "contraseña").send_keys(existing_user_credentials['contraseña'])
        driver.find_element(By.ID, "btn-ingresar").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "usuario-logueado")))

        # Logout
        driver.find_element(By.ID, "btn-cerrar-sesion").click()
        wait.until(EC.url_contains(f"{app_url}/"))

        # Verificar que localStorage está limpio
        local_storage = driver.execute_script("return window.localStorage.length")
        assert local_storage == 0

    def test_rf_05_03_cannot_access_protected_pages_after_logout(self, driver, app_url, existing_user_credentials, wait):
        """
        CP-RF-05-03: Verificar que no se puede acceder a páginas protegidas sin sesión.
        """
        # Login
        driver.get(f"{app_url}/login")
        wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(existing_user_credentials['email'])
        driver.find_element(By.ID, "contraseña").send_keys(existing_user_credentials['contraseña'])
        driver.find_element(By.ID, "btn-ingresar").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "usuario-logueado")))

        # Logout
        driver.find_element(By.ID, "btn-cerrar-sesion").click()
        wait.until(EC.url_contains(f"{app_url}/"))

        # Intentar acceder a página protegida
        driver.get(f"{app_url}/mi-cuenta")

        # Debe redirigir al login
        wait.until(EC.url_contains(f"{app_url}/login"))
        assert "login" in driver.current_url.lower()
