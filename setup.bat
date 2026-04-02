@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo === ComicStore: configuracion inicial ===
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: No se encontro "python" en el PATH. Instala Python 3.10+ desde https://www.python.org/
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creando entorno virtual .venv ...
  python -m venv .venv
  if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual.
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo ERROR: Fallo pip install.
  exit /b 1
)

echo.
echo Aplicando migraciones...
python manage.py migrate --noinput
if errorlevel 1 exit /b 1

echo.
echo Recolectando archivos estaticos...
python manage.py collectstatic --noinput
if errorlevel 1 exit /b 1

echo.
echo Cargando pasarelas de pago en la base de datos...
python cargar_pasarelas.py
if errorlevel 1 exit /b 1

echo.
echo === Listo ===
echo Entorno: .venv  ^(activar con: .venv\Scripts\activate.bat^)
echo Siguiente paso: ejecuta run.bat para iniciar el servidor de desarrollo.
echo.
echo Datos opcionales ^(solo si aun no los cargaste^):
echo   python agregar_pais.py
echo   python cargar_regiones.py
echo   python cargar_comunas.py
echo   python cargar_comics.py
echo   python manage.py createsuperuser
echo.
pause
endlocal
