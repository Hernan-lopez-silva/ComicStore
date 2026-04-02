@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
  echo ERROR: No existe el entorno virtual. Ejecuta primero setup.bat
  pause
  exit /b 1
)

call ".venv\Scripts\activate.bat"
echo Iniciando servidor en http://127.0.0.1:8000/
echo Ctrl+C para detener.
echo.
python manage.py runserver
set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" pause
endlocal
exit /b %ERR%
