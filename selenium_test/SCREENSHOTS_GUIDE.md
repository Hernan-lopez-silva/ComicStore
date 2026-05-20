# 📸 Guía de Screenshots en Tests

## Cómo Funcionan

Los tests ahora capturan screenshots automáticamente en **puntos clave** para documentar el flujo de prueba.

### ✅ Captura Automática en Fallos

Si un test falla, se captura automáticamente una pantalla con el estado del fallo:

```
screenshots/
├── FAILURE_test_rf_01_01_successful_registration_20260519_143022.png
├── FAILURE_test_rf_02_03_login_fails_20260519_143045.png
└── ...
```

### 🎯 Captura Manual en Puntos Clave

En los tests, puedes capturar screenshots en puntos estratégicos:

```python
def test_rf_01_01_successful_registration(driver, app_url, capture_screenshot):
    # Paso 1: Página inicial
    driver.get(f"{app_url}/registro")
    capture_screenshot("paso1_pagina_registro")
    
    # Paso 2: Completar formulario
    driver.find_element(By.ID, "nombre").send_keys("Juan")
    driver.find_element(By.ID, "email").send_keys("test@example.com")
    capture_screenshot("paso2_formulario_completo")
    
    # Paso 3: Resultado
    driver.find_element(By.ID, "btn-registrarse").click()
    wait.until(EC.url_contains("/"))
    capture_screenshot("paso3_registro_exitoso")
```

## 📁 Estructura de Archivos

```
selenium_test/
└── screenshots/              ← Se crea automáticamente
    ├── test_rf_01_01_paso1_pagina_registro_20260519_143022.png
    ├── test_rf_01_01_paso2_formulario_completo_20260519_143022.png
    ├── test_rf_01_01_paso3_registro_exitoso_20260519_143022.png
    ├── test_rf_02_01_paso1_pagina_login_20260519_143045.png
    ├── FAILURE_test_rf_02_03_login_fails_20260519_143100.png
    └── ...
```

## 🎬 Ejecución

### Ver logs de capturas durante ejecución

```bash
pytest -v -s test_authentication.py
```

**Salida esperada:**
```
test_authentication.py::TestRegistration::test_rf_01_01_successful_registration PASSED
screenshots/test_rf_01_01_paso1_pagina_registro_20260519_143022.png
screenshots/test_rf_01_01_paso2_formulario_completo_20260519_143022.png
screenshots/test_rf_01_01_paso3_registro_exitoso_20260519_143022.png
```

### Ejecutar un test específico y ver screenshots

```bash
pytest test_authentication.py::TestRegistration::test_rf_01_01_successful_registration -v -s
```

### Ver screenshots después de la ejecución

```bash
# Windows
explorer selenium_test\screenshots

# Mac
open selenium_test/screenshots

# Linux
nautilus selenium_test/screenshots
```

## 🔍 Puntos Clave donde Capturar

### Autenticación (RF-01, RF-02, RF-05)
- ✅ Página de registro/login inicial
- ✅ Formulario completado antes de enviar
- ✅ Mensaje de éxito/error
- ✅ Redirección completada

### Catálogo (RF-06 a RF-10)
- ✅ Listado de productos
- ✅ Detalle del producto abierto
- ✅ Formulario de búsqueda con resultados
- ✅ Filtros aplicados

### Carrito (RF-03, RF-04, RF-11)
- ✅ Carrito con items
- ✅ Producto agregado
- ✅ Cantidad modificada
- ✅ Item removido

### Checkout (RF-12, RF-13)
- ✅ Carrito antes de checkout
- ✅ Resumen del pedido
- ✅ Dirección de envío completada
- ✅ Cupón aplicado
- ✅ Confirmación final

## 💾 Ejemplos Implementados

Ya hay ejemplos de capturas en:

```
test_authentication.py
├── test_rf_01_01_successful_registration (3 capturas)
└── test_rf_02_01_successful_login (3 capturas)

test_catalog.py
└── test_rf_06_01_view_product_detail (2 capturas)

test_cart_and_checkout.py
└── test_rf_12_01_checkout_shows_order_summary (2 capturas)
```

## 🎨 Nombres de Capturas Recomendados

```python
capture_screenshot("paso1_pagina_inicial")      # Punto de partida
capture_screenshot("paso2_formulario_lleno")    # Después de llenar
capture_screenshot("paso3_validacion_error")    # Error si ocurre
capture_screenshot("paso4_exito")               # Resultado exitoso
capture_screenshot("paso5_confirmacion")        # Confirmación final
```

## ⚡ Buenas Prácticas

1. **Captura solo en pasos principales** - No todos los clics necesitan screenshot
2. **Nombra descriptivamente** - Usa `paso1_`, `paso2_`, etc.
3. **Antes y después de acciones** - Captura antes de click y después del resultado
4. **Errores importantes** - Captura cuando ocurren validaciones o errores
5. **Resultado final** - Siempre captura el estado final del flujo

## 🚀 Automatización Completa

La fixture `screenshot_on_failure` captura automáticamente cuando un test falla:

```python
# No necesitas hacer nada especial - es automático
def test_rf_03_03_add_product_exceeding_stock_fails(self, driver, app_url, wait):
    driver.get(f"{app_url}/catalogo")
    # ... si falla aquí, se captura automáticamente
    assert len(productos) > 0  # Si esto falla, screenshot automático
```

## 📊 Análisis de Screenshots

Después de la ejecución:

```bash
# Contar total de screenshots
ls -1 screenshots/ | wc -l

# Ver solo capturas de éxito
ls screenshots/ | grep -v FAILURE

# Ver solo capturas de fallos
ls screenshots/ | grep FAILURE

# Eliminar todas las capturas
rm -rf screenshots/
```

## 📝 Integración con Reportes

Con pytest-html:

```bash
pytest --html=report.html --self-contained-html
```

El reporte HTML puede incluir referencias a los screenshots.

---

**Nota**: Los screenshots se guardan con timestamp para evitar sobrescrituras entre ejecuciones.
