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
