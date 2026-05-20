# ComicStore

Aplicacion web desarrollada con Django para la venta de comics en linea.

Incluye catalogo, carrito de compras, checkout, autenticacion/registro, panel administrativo y carga de datos base (pais, regiones, comunas, comics y pasarelas).

## Requisitos del aplicativo

- Python `3.10` a `3.12` (recomendado: `3.11.x`)
- `pip` actualizado
- Git (opcional, para clonar/versionar)
- SQLite (integrado en Python)
- En Windows: PowerShell o CMD

Dependencias Python principales (ver `requirements.txt`):
- Django `>=4.2.13,<5`
- djangorestframework `>=3.15.1,<4`
- whitenoise, dj-database-url, gunicorn

## Estructura relevante

- `manage.py`: comandos de administracion Django
- `setup.bat`: primer arranque en Windows (`venv` + instalacion + migraciones + `collectstatic` + pasarelas)
- `run.bat`: ejecucion local en desarrollo
- `cargar_pasarelas.py`: carga pasarelas de pago
- `agregar_pais.py`: carga pais base (Chile)
- `cargar_regiones.py`: carga regiones
- `cargar_comunas.py`: carga comunas
- `cargar_comics.py`: carga comics iniciales

## Levantamiento completo (primer arranque)

### Opcion recomendada (Windows con scripts del proyecto)

1. Clona el repositorio y entra a la carpeta del proyecto.
2. Ejecuta la configuracion inicial:

```bat
.\setup.bat
```

Esto realiza automaticamente:
- creacion de `.venv`
- instalacion de dependencias
- migraciones
- `collectstatic`
- carga de pasarelas

3. Carga tablas/datos base (si aun no existen):

```bat
.\.venv\Scripts\python.exe agregar_pais.py
.\.venv\Scripts\python.exe cargar_regiones.py
.\.venv\Scripts\python.exe cargar_comunas.py
.\.venv\Scripts\python.exe cargar_comics.py
```

4. Inicia la aplicacion:

```bat
.\run.bat
```

5. Abre en navegador:

- `http://127.0.0.1:8000/`

## Levantamiento manual (alternativa)

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python cargar_pasarelas.py
python agregar_pais.py
python cargar_regiones.py
python cargar_comunas.py
python cargar_comics.py
python manage.py runserver
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python cargar_pasarelas.py
python agregar_pais.py
python cargar_regiones.py
python cargar_comunas.py
python cargar_comics.py
python manage.py runserver
```

## Superusuario (admin)

Crear manualmente:

```bash
python manage.py createsuperuser
```

## Archivos estaticos y Git

`staticfiles/` es salida generada por `collectstatic`, por lo que **no debe versionarse**.

## API de ubicaciones (registro)

Endpoints disponibles:

- `GET /pais`
- `GET /region/{id_pais}`
- `GET /comuna/{id_region}`

Ejemplos locales:

- `http://127.0.0.1:8000/pais`
- `http://127.0.0.1:8000/region/1`
- `http://127.0.0.1:8000/comuna/1`

## Despliegue de referencia

- URL: `https://comicstore.up.railway.app/`
- Entorno PythonAnywhere: `http://jsaavedrap.pythonanywhere.com/`

## Pruebas Automatizadas (Selenium)

El proyecto incluye 37 pruebas automatizadas de interfaz de usuario (UI) que verifican el correcto funcionamiento de los flujos principales (Login, Carrito, Búsqueda y Registro).

### Ejecutar Pruebas Localmente

Asegúrate de que el servidor de desarrollo esté corriendo:
```powershell
# En una terminal:
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

En **otra terminal**, activa tu entorno virtual y ejecuta las pruebas individualmente:
```powershell
.\.venv\Scripts\Activate.ps1

python selenium_tests\test_login.py
python selenium_tests\test_carrito.py
python selenium_tests\test_busqueda.py
python selenium_tests\test_registro.py
```

O ejecútalas todas juntas usando `pytest` (usar bandera `-s` para ver el log paso a paso y evitar conflictos con la consola):
```powershell
pytest selenium_tests\ -v -s
```

### Ejecutar Pruebas contra Producción (PythonAnywhere)

Los scripts están configurados para correr localmente (`http://127.0.0.1:8000`) por defecto. Si el ambiente de producción (`http://jsaavedrap.pythonanywhere.com/`) está activo y quieres apuntar las pruebas hacia allá, puedes usar la variable de entorno `TEST_BASE_URL`.

**En Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
$env:TEST_BASE_URL="http://jsaavedrap.pythonanywhere.com"
pytest selenium_tests\ -v -s
```

**En Windows (CMD):**
```cmd
.\.venv\Scripts\activate.bat
set TEST_BASE_URL=http://jsaavedrap.pythonanywhere.com
pytest selenium_tests\ -v -s
```

*Nota: Para que las pruebas pasen en producción, la base de datos de producción debe tener cargados los cómics base y el usuario de pruebas `testuser`.*

## Pruebas de Carga y Estrés (Locust)

El proyecto incorpora pruebas de carga automatizadas mediante **Locust** que simulan el comportamiento de múltiples usuarios concurrentes interactuando con los módulos principales de ComicStore.

### Características del Script de Carga:
- **Autenticación Automática (Login):** Simula el inicio de sesión del usuario de prueba (`testuser`), gestionando de manera dinámica las cookies y el token de seguridad `csrfmiddlewaretoken` de Django.
- **Flujos Ponderados (Weights):** Simula navegación general por la home, búsquedas de productos de interés, vista de detalle de cómics y revisión del carrito de compras.
- **Trazas en Consola:** Cada acción realizada por los usuarios virtuales deja un log explicativo detallado en consola, ideal para auditorías o evidencias.

### Requisitos Previos
1. Tener el servidor local corriendo en `http://127.0.0.1:8000/`.
2. Tener instalado Locust en tu entorno virtual (`pip install -r requirements.txt`).

### Ejecución de Pruebas

#### Opción 1: Con interfaz web interactiva
Para configurar la simulación de forma visual e interactiva:

1. Ejecuta el comando en tu terminal (con tu entorno virtual activo):
   ```powershell
   locust
   ```
2. Abre tu navegador en la URL: **`http://localhost:8089`**
3. Define los siguientes parámetros iniciales:
   - **Number of users:** Cantidad máxima de usuarios concurrentes (ej. `50`).
   - **Spawn rate:** Cantidad de usuarios creados por segundo (ej. `5`).
   - **Host:** La URL del servidor local: `http://127.0.0.1:8000`
4. Haz clic en **Start swarming** para ver los gráficos de rendimiento en tiempo real.

#### Opción 2: Modo No-Interactivo (Headless) - Generación de Evidencia 📄
Esta opción ejecuta las pruebas de forma automática durante un tiempo definido y exporta un **reporte HTML detallado** y gráficos completos directamente a la carpeta `reports/` como evidencia del análisis de rendimiento.

Ejecuta el siguiente comando en tu terminal de PowerShell:
```powershell
.venv\Scripts\locust.exe --headless -u 20 -r 2 --run-time 1m --html reports/locust_report.html
```

*Parámetros del comando:*
- `-u 20`: Simula 20 usuarios simultáneos.
- `-r 2`: Agrega 2 nuevos usuarios por segundo hasta llegar al máximo.
- `--run-time 1m`: Duración total de la prueba (1 minuto).
- `--html reports/locust_report.html`: Ubicación y nombre del archivo de reporte HTML generado como evidencia del análisis.
