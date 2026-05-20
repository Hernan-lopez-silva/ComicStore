import logging
from locust import HttpUser, task, between

# Configurar logs
logger = logging.getLogger("locust_comicstore")
logging.basicConfig(level=logging.INFO)

class ComicStoreLoadTestUser(HttpUser):
    # Host por defecto (servidor local)
    host = "http://127.0.0.1:8000"
    # Tiempo de espera aleatorio entre 1 y 3 segundos por usuario
    wait_time = between(1, 3)

    def on_start(self):
        """Se ejecuta al iniciar cada usuario simulado (Login)."""
        logger.info("---- [INICIO] Simulación de inicio de sesión de usuario ----")
        
        # 1. Obtener la página de login para registrar cookies y CSRF token
        response = self.client.get("/login/", name="/login [GET]")
        if response.status_code == 200:
            csrf_token = self.client.cookies.get("csrftoken")
            if csrf_token:
                logger.info(f"CSRF token obtenido con éxito: {csrf_token[:8]}...")
                
                # 2. Enviar el formulario de autenticación POST
                payload = {
                    "username": "testuser",
                    "password": "TestPass123!",
                    "csrfmiddlewaretoken": csrf_token
                }
                headers = {
                    "X-CSRFToken": csrf_token,
                    "Referer": self.client.base_url + "/login/"
                }
                
                login_resp = self.client.post("/login/", data=payload, headers=headers, name="/login [POST]")
                if login_resp.status_code == 200 and "/login" not in login_resp.url:
                    logger.info("¡Inicio de sesión simulación EXITOSA!")
                else:
                    logger.warning("Simulación de inicio de sesión fallida o redirigida incorrectamente.")
            else:
                logger.error("No se pudo extraer el CSRF token de las cookies.")
        else:
            logger.error(f"Fallo al cargar la página de login. Código: {response.status_code}")

    @task(4)
    def ver_home(self):
        """Simula a un usuario navegando por la página de inicio."""
        logger.info("Usuario simulado: Visitando la página de inicio (/)")
        self.client.get("/", name="/")

    @task(3)
    def buscar_comics(self):
        """Simula a un usuario realizando búsquedas de cómics."""
        terminos = ["batman", "spiderman", "comics"]
        for termino in terminos:
            logger.info(f"Usuario simulado: Buscando el término '{termino}'")
            self.client.get(f"/?q={termino}", name="/buscar")

    @task(2)
    def ver_detalle_producto(self):
        """Simula a un usuario viendo el detalle de un cómic en particular."""
        logger.info("Usuario simulado: Viendo detalle de producto con id=1")
        self.client.get("/producto/?id=1", name="/producto")

    @task(2)
    def ver_carrito(self):
        """Simula a un usuario revisando el contenido de su carrito."""
        logger.info("Usuario simulado: Visualizando carrito de compras (/carrito/)")
        self.client.get("/carrito/", name="/carrito")
