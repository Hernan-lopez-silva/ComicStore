# Tests Selenium - ComicStore

Suite de pruebas automatizadas con Selenium y pytest para la aplicación ComicStore.

## Estructura de Carpetas

```
selenium_test/
├── conftest.py              # Fixtures compartidas y configuración
├── test_authentication.py   # Tests de autenticación (RF-01, RF-02, RF-05)
├── test_catalog.py          # Tests de catálogo (RF-06, RF-07, RF-08, RF-09, RF-10)
├── test_cart_and_checkout.py # Tests de carrito y compra (RF-03, RF-04, RF-11, RF-12, RF-13)
├── pytest.ini               # Configuración de pytest
├── requirements.txt         # Dependencias del proyecto
└── README.md               # Este archivo
```

## Requerimientos Funcionales Cubiertos

### Autenticación (RF-01, RF-02, RF-05)
- **RF-01**: Registro de nuevo usuario
  - CP-RF-01-01: Registro exitoso con datos válidos
  - CP-RF-01-02: Aceptación de diferentes formatos de email
  - CP-RF-01-03: Rechazo de emails inválidos

- **RF-02**: Login de usuario
  - CP-RF-02-01: Login exitoso con credenciales válidas
  - CP-RF-02-02: Fallo con contraseña incorrecta
  - CP-RF-02-03: Fallo con email no registrado

- **RF-05**: Cierre de sesión
  - CP-RF-05-01: Logout exitoso
  - CP-RF-05-02: Limpieza de datos de sesión
  - CP-RF-05-03: No acceso a páginas protegidas tras logout

### Catálogo de Productos (RF-06, RF-07, RF-08, RF-09, RF-10)
- **RF-06**: Ver detalle de producto
  - CP-RF-06-01: Visualizar detalle de producto válido
  - CP-RF-06-02: Mostrar toda la información del producto
  - CP-RF-06-03: Error con ID inválido

- **RF-07**: Crear producto (Admin)
  - CP-RF-07-01: Crear producto con datos válidos
  - CP-RF-07-02: Validación de campos requeridos
  - CP-RF-07-03: Validación de precio

- **RF-08**: Actualizar producto (Admin)
  - CP-RF-08-01: Actualizar producto con datos válidos
  - CP-RF-08-02: Preservación de otros campos
  - CP-RF-08-03: Validación de stock

- **RF-09**: Eliminar producto (Admin)
  - CP-RF-09-01: Eliminar producto
  - CP-RF-09-02: Requiere confirmación
  - CP-RF-09-03: Cancelar preserva producto

- **RF-10**: Búsqueda de productos
  - CP-RF-10-01: Búsqueda retorna resultados relevantes
  - CP-RF-10-02: Mensaje cuando no hay resultados
  - CP-RF-10-03: Búsqueda insensible a mayúsculas

### Carrito de Compras (RF-03, RF-04, RF-11)
- **RF-03**: Agregar producto al carrito
  - CP-RF-03-01: Agregar con cantidad válida
  - CP-RF-03-02: Diferentes cantidades válidas
  - CP-RF-03-03: Fallo al exceder stock

- **RF-04**: Eliminar producto del carrito
  - CP-RF-04-01: Eliminar producto
  - CP-RF-04-02: Vaciar carrito
  - CP-RF-04-03: Cancelar elimina

- **RF-11**: Modificar cantidad en carrito
  - CP-RF-11-01: Actualizar cantidad
  - CP-RF-11-02: Diferentes cantidades válidas
  - CP-RF-11-03: Fallo al exceder stock

### Checkout (RF-12, RF-13)
- **RF-12**: Resumen de pedido y checkout
  - CP-RF-12-01: Mostrar resumen del pedido
  - CP-RF-12-02: Ingreso de dirección de envío
  - CP-RF-12-03: Cálculo correcto de totales

- **RF-13**: Descuentos y cupones
  - CP-RF-13-01: Aplicar cupón válido
  - CP-RF-13-02: Error con cupón inválido
  - CP-RF-13-03: Error con cupón expirado

**Total: 39 casos de prueba (13 RF × 3 casos cada uno)**

## Instalación

### 1. Clonar o descargar el proyecto

```bash
cd selenium_test
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configuración

Editar variables de entorno en `conftest.py` si es necesario:
- `app_url`: URL de la aplicación (default: http://localhost:8000)
- Credenciales de usuario para tests de login

## Ejecución de Tests

### Ejecutar todos los tests

```bash
pytest
```

### Ejecutar tests con salida verbose

```bash
pytest -v
```

### Ejecutar tests de un módulo específico

```bash
pytest test_authentication.py
pytest test_catalog.py
pytest test_cart_and_checkout.py
```

### Ejecutar tests por categoría (markers)

```bash
# Solo tests de autenticación
pytest -m authentication

# Solo tests de catálogo
pytest -m catalog

# Solo tests de carrito
pytest -m cart

# Solo tests críticos
pytest -m smoke

# Excluir tests lentos
pytest -m "not slow"
```

### Ejecutar en paralelo (más rápido)

```bash
pytest -n auto
```

### Ejecutar con reporte HTML

```bash
pytest --html=report.html --self-contained-html
```

### Ejecutar con cobertura

```bash
pytest --cov=. --cov-report=html
```

### Ejecutar solo último test que falló

```bash
pytest --lf
```

### Ejecutar y parar en primer fallo

```bash
pytest -x
```

## Estructura de Fixtures

### Fixtures de Navegador
- `driver`: Instancia del navegador para cada test
- `wait`: WebDriverWait configurado
- `wait_short`: WebDriverWait más corto

### Fixtures de Datos
- `valid_user_data`: Datos válidos de usuario
- `existing_user_credentials`: Credenciales existentes
- `comic_product`: Datos de producto
- `shipping_address`: Dirección de envío
- `payment_data`: Datos de pago
- `coupon_data`: Cupones de descuento

### Fixtures de Utilidad
- `capture_screenshot`: Captura pantalla en caso de fallo
- `log_browser_errors`: Registra errores del navegador

## Convenciones de Nombres

- **Archivo**: `test_<modulo>.py`
- **Clase**: `Test<Funcionalidad>` (ej: `TestAuthentication`)
- **Función**: `test_rf_<XX>_<YY>_<descripcion>` 
  - XX: Número de RF
  - YY: Número de caso de prueba
  - descripcion: Descripción breve

Ejemplo: `test_rf_01_01_successful_registration_with_valid_data`

## Mejores Prácticas Aplicadas

1. **Waits Explícitos**: Usar `WebDriverWait` con `EC` en lugar de `time.sleep()`
2. **Fixtures de Datos**: Datos reutilizables y mantenibles
3. **Parametrización**: `@pytest.mark.parametrize` para casos similares
4. **Limpieza Automática**: Cookies y localStorage se limpian entre tests
5. **Nombres Descriptivos**: Tests se entienden sin leer el código
6. **Un Concepto por Test**: Cada test verifica una cosa específica
7. **Markers**: Categorización de tests para ejecución selectiva
8. **Logging**: Logs de navegador capturados automáticamente

## Troubleshooting

### Tests no encuentran elementos
- Verificar que los IDs y selectores CSS/XPath corresponden a la aplicación
- Usar `wait.until()` en lugar de `driver.find_element()` directamente
- Aumentar timeout en `conftest.py` si es necesario

### ChromeDriver issues
- `webdriver-manager` descarga automáticamente el driver correcto
- Si hay problemas, reinstalar: `pip install --force-reinstall webdriver-manager`

### URL incorrecta
- Editar `app_url` en fixture `app_url` de `conftest.py`
- O pasar por variable de entorno: `APP_URL=http://localhost:3000 pytest`

### Tests lentos
- Verificar que `--headless` está habilitado en `conftest.py`
- Ejecutar en paralelo: `pytest -n auto`
- Aumentar timeout de load: `driver.set_page_load_timeout()`

## Integración Continua

Para usar en CI/CD (GitHub Actions, Jenkins, etc.):

```yaml
- name: Run Selenium Tests
  run: |
    pip install -r selenium_test/requirements.txt
    pytest selenium_test/ --html=report.html
```

## Autores y Contacto

Generado con pytest-patterns skill para ComicStore
Email: her.lopezs@duocuc.cl
Fecha: 2026-05-19
