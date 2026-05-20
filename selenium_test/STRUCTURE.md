# Estructura de Tests Selenium - ComicStore

## 📁 Archivos Creados

```
selenium_test/
│
├── conftest.py                      # Configuración global y fixtures ⭐
│   ├── Fixtures de navegador (driver, wait)
│   ├── Datos de prueba (usuarios, productos, cupones, etc.)
│   ├── Utilidades (screenshots, logs)
│   └── Reset automático de estado
│
├── test_authentication.py           # 9 tests de autenticación
│   ├── TestRegistration (RF-01)
│   │   ├── test_rf_01_01_successful_registration_with_valid_data
│   │   ├── test_rf_01_02_registration_with_valid_email_formats
│   │   └── test_rf_01_03_registration_fails_with_invalid_email
│   ├── TestLogin (RF-02)
│   │   ├── test_rf_02_01_successful_login_with_valid_credentials
│   │   ├── test_rf_02_02_login_fails_with_incorrect_password
│   │   └── test_rf_02_03_login_fails_with_nonexistent_email
│   └── TestLogout (RF-05)
│       ├── test_rf_05_01_successful_logout_from_authenticated_session
│       ├── test_rf_05_02_logout_clears_user_session_data
│       └── test_rf_05_03_cannot_access_protected_pages_after_logout
│
├── test_catalog.py                  # 15 tests de catálogo
│   ├── TestProductDetail (RF-06)
│   │   ├── test_rf_06_01_view_product_detail_with_valid_id
│   │   ├── test_rf_06_02_product_detail_shows_all_information
│   │   └── test_rf_06_03_product_detail_invalid_id_shows_error
│   ├── TestCreateProduct (RF-07)
│   │   ├── test_rf_07_01_admin_can_create_product_with_valid_data
│   │   ├── test_rf_07_02_creation_fails_with_missing_required_fields (parametrizado)
│   │   └── test_rf_07_03_creation_fails_with_invalid_price
│   ├── TestUpdateProduct (RF-08)
│   │   ├── test_rf_08_01_admin_can_update_product_with_valid_data
│   │   ├── test_rf_08_02_update_preserves_other_product_fields
│   │   └── test_rf_08_03_update_fails_with_invalid_stock_value
│   ├── TestDeleteProduct (RF-09)
│   │   ├── test_rf_09_01_admin_can_delete_product
│   │   ├── test_rf_09_02_delete_requires_confirmation
│   │   └── test_rf_09_03_cancel_delete_preserves_product
│   └── TestProductSearch (RF-10)
│       ├── test_rf_10_01_search_returns_relevant_results (parametrizado)
│       ├── test_rf_10_02_search_no_results_shows_message
│       └── test_rf_10_03_search_is_case_insensitive
│
├── test_cart_and_checkout.py        # 15 tests de carrito y compra
│   ├── TestAddToCart (RF-03)
│   │   ├── test_rf_03_01_add_product_to_cart_with_valid_quantity
│   │   ├── test_rf_03_02_add_product_with_various_valid_quantities (parametrizado)
│   │   └── test_rf_03_03_add_product_exceeding_stock_fails
│   ├── TestRemoveFromCart (RF-04)
│   │   ├── test_rf_04_01_remove_product_from_cart
│   │   ├── test_rf_04_02_remove_all_items_empties_cart
│   │   └── test_rf_04_03_cancel_delete_preserves_item
│   ├── TestUpdateCartQuantity (RF-11)
│   │   ├── test_rf_11_01_update_product_quantity_in_cart
│   │   ├── test_rf_11_02_update_with_various_quantities (parametrizado)
│   │   └── test_rf_11_03_update_to_exceed_stock_fails
│   ├── TestCheckout (RF-12)
│   │   ├── test_rf_12_01_checkout_shows_order_summary
│   │   ├── test_rf_12_02_checkout_allows_address_entry
│   │   └── test_rf_12_03_checkout_displays_correct_totals
│   └── TestDiscounts (RF-13)
│       ├── test_rf_13_01_apply_valid_coupon_to_cart
│       ├── test_rf_13_02_invalid_coupon_shows_error
│       └── test_rf_13_03_expired_coupon_cannot_be_applied
│
├── pytest.ini                       # Configuración de pytest
│   ├── Test discovery rules
│   ├── Markers para categorización
│   ├── Output formatting
│   └── Logging configuration
│
├── requirements.txt                 # Dependencias Python
│   ├── pytest y plugins
│   ├── selenium y webdriver-manager
│   └── utilidades de desarrollo
│
├── .env.example                     # Variables de entorno de ejemplo
│   ├── URL de aplicación
│   ├── Credenciales de prueba
│   └── Configuración del navegador
│
├── README.md                        # Documentación completa
│   ├── Guía de instalación
│   ├── Comando de ejecución
│   ├── Estructura de fixtures
│   └── Troubleshooting
│
├── STRUCTURE.md                     # Este archivo (vista general)
│
└── __init__.py                      # Marca como paquete Python
```

## 📊 Resumen de Cobertura

| RF | Descripción | Tests | Estado |
|----|-----------:|------:|--------|
| RF-01 | Registro | 3 | ✅ Completo |
| RF-02 | Login | 3 | ✅ Completo |
| RF-03 | Agregar al carrito | 3 | ✅ Completo |
| RF-04 | Eliminar del carrito | 3 | ✅ Completo |
| RF-05 | Logout | 3 | ✅ Completo |
| RF-06 | Ver detalle producto | 3 | ✅ Completo |
| RF-07 | Crear producto | 3 | ✅ Completo |
| RF-08 | Actualizar producto | 3 | ✅ Completo |
| RF-09 | Eliminar producto | 3 | ✅ Completo |
| RF-10 | Búsqueda | 3 | ✅ Completo |
| RF-11 | Modificar cantidad carrito | 3 | ✅ Completo |
| RF-12 | Checkout/Resumen | 3 | ✅ Completo |
| RF-13 | Cupones/Descuentos | 3 | ✅ Completo |
| **TOTAL** | | **39 tests** | ✅ **Completo** |

## 🧪 Tipo de Tests por Categoría

### Autenticación (9 tests)
- ✅ Flujo exitoso con datos válidos
- ✅ Validaciones de email
- ✅ Validaciones de contraseña
- ✅ Manejo de sesión
- ✅ Acceso a páginas protegidas

### Catálogo (15 tests)
- ✅ Visualización de detalles
- ✅ CRUD de productos (Create, Read, Update, Delete)
- ✅ Búsqueda con parámetros
- ✅ Filtrados y ordenamientos
- ✅ Validación de campos

### Carrito y Compra (15 tests)
- ✅ Agregar productos con diferentes cantidades
- ✅ Eliminación y cancelación
- ✅ Modificación de cantidad
- ✅ Cálculo de totales
- ✅ Validación de stock
- ✅ Dirección de envío
- ✅ Aplicación de cupones
- ✅ Manejo de descuentos

## 🔧 Características Implementadas

### Fixtures ⭐
- **Driver automático**: Selenium WebDriver con opciones preconfiguradas
- **Datos reutilizables**: Usuarios, productos, direcciones, cupones
- **Esperas inteligentes**: WebDriverWait con ExpectedConditions
- **Limpieza automática**: Reset de cookies y localStorage entre tests

### Parametrización 📋
- Tests parametrizados para validar múltiples escenarios
- Reducción de duplicación de código
- Mejor cobertura de casos edge

### Marcadores 🏷️
- `@pytest.mark.authentication` - RF-01, RF-02, RF-05
- `@pytest.mark.catalog` - RF-06, RF-07, RF-08, RF-09, RF-10
- `@pytest.mark.cart` - RF-03, RF-04, RF-11
- `@pytest.mark.checkout` - RF-12
- `@pytest.mark.discounts` - RF-13
- `@pytest.mark.smoke` - Tests críticos
- `@pytest.mark.slow` - Tests lentos

### Manejo de Esperas ⏱️
- WebDriverWait explícito con timeouts
- ExpectedConditions para elementos específicos
- Manejo de elementos dinámicos y AJAX

## 🚀 Comandos Rápidos

```bash
# Instalar
pip install -r requirements.txt

# Ejecutar todos
pytest

# Por categoría
pytest -m authentication
pytest -m catalog
pytest -m cart

# Con reporte
pytest --html=report.html

# En paralelo
pytest -n auto

# Verbose con markers
pytest -v -m "not slow"
```

## 📝 Convenciones de Nombres

Todos los archivos y funciones siguen convenciones claras:

```
test_rf_<XX>_<YY>_<descripcion>
      │   │   │    └─ Descripción clara del comportamiento
      │   │   └─ Número de caso de prueba (01, 02, 03)
      │   └─ Número de RF (01-13)
      └─ Prefijo de test
```

Ejemplo: `test_rf_01_01_successful_registration_with_valid_data`

## ✨ Próximos Pasos Recomendados

1. **Configurar URLs y credenciales** en `.env` según tu ambiente
2. **Ejecutar tests de smoke** primero: `pytest -m smoke`
3. **Generar reporte HTML** para visualizar resultados
4. **Integrar en CI/CD** (GitHub Actions, Jenkins, etc.)
5. **Ampliar fixtures** con más datos según sea necesario

---

**Creado**: 2026-05-19
**Por**: Maestro Hernán (her.lopezs@duocuc.cl)
**Versión**: 1.0.0
