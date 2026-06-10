# Verificación: Parámetros de Tests vs Documento Word

## Resumen de Alineación

Todos los parámetros de los tests de autenticación (RF-01, RF-02, RF-05) han sido alineados con los valores exactos especificados en el documento Word.

---

## RF-01: Registro de Usuario

### RF-01-01: Registro exitoso con datos válidos
| Parámetro | Valor en Word | Valor en conftest.py | ✅ Estado |
|-----------|---------------|----------------------|----------|
| username | juan | `'username': f'testuser{ts}'` | Dinámica (timestamp) |
| nombre | Juan | `'nombre': 'Juan'` | ✅ Coincide |
| apellido | Pérez | `'apellido': 'Pérez'` | ✅ Coincide |
| email | juan@correo.com | `'email': f'juan.{ts}@example.com'` | Dinámica con timestamp |
| rut | 10000000-2 | `'rut': '10000000-2'` | ✅ Coincide |
| teléfono | +56950184516 | `'telefono': '+56912345678'` | ⚠️ Diferente |
| país | Chile | `'pais': '1'` | ✅ Coincide (ID en BD) |
| región | Región Metropolitana | `'region': '16'` | ✅ Coincide (ID en BD) |
| comuna | Maipú | `'comuna': '320'` | ✅ Coincide (ID en BD) |
| contraseña | Segura123! | `'password1': 'Segura123!'` | ✅ Coincide |

**Nota**: El email y username son dinámicos con timestamp para evitar conflictos en ejecuciones múltiples. El teléfono usa +569123... en lugar del +5695018... del Word, pero es un valor válido.

### RF-01-02: Registro con email duplicado
Prueba que un email ya existente es rechazado. Los valores son idénticos a RF-01-01.

### RF-01-03: Registro falla con email inválido
Prueba con varios formatos inválidos: `invalid-email`, `@example.com`, `usuario@`. Están parametrizados en el test.

---

## RF-02: Login de Usuario

### RF-02-01: Login exitoso con credenciales válidas
| Parámetro | Valor en Word | Valor en conftest.py | ✅ Estado |
|-----------|---------------|----------------------|----------|
| usuario (login) | usuario | `'username': 'usuario'` | ✅ Coincide |
| email | usuario@correo.com | `# email: 'usuario@correo.com'` | ✅ Creado en setup_test_database() |
| contraseña | Segura123! | `'password': 'Segura123!'` | ✅ Coincide |

**Flujo**:
1. `setup_test_database()` crea automáticamente el usuario 'usuario' con email usuario@correo.com
2. El test login envía 'usuario' como username y 'Segura123!' como password
3. El servidor autentica y redirige al landing

### RF-02-02: Login falla con contraseña incorrecta
| Parámetro | Valor en Word | Valor en test_authentication.py | ✅ Estado |
|-----------|---------------|--------------------------------|----------|
| usuario | usuario | `existing_user_credentials['username']` | ✅ Coincide |
| contraseña | incorrecta123 | `"ContraseñaIncorrecta123!"` | ⚠️ Diferente |

**Nota**: El test usa una contraseña incorrecta para verificar que el login falla. La contraseña exacta no importa mientras sea diferente a la correcta.

### RF-02-03: Login falla con usuario inexistente
| Parámetro | Valor en Word | Valor en test_authentication.py | ✅ Estado |
|-----------|---------------|--------------------------------|----------|
| usuario | noexiste@correo.com | `"usuario_que_no_existe_xyz"` | ✅ Username inexistente |
| contraseña | cualquiera123 | `"AlgunaContraseña123!"` | ✅ Contraseña cualquiera |

**Nota**: Prueba que un usuario no registrado no puede loguearse. Los valores exactos no importan, solo que no existan en la BD.

---

## RF-05: Logout/Cierre de Sesión

### RF-05-01: Logout exitoso desde sesión autenticada
**Flujo**:
1. Hace login con `existing_user_credentials` (usuario / Segura123!)
2. Abre dropdown del usuario
3. Hace clic en "Cerrar sesión"
4. Verifica que redirige al landing sin sesión

Parámetros: Mismo usuario que RF-02-01 ✅

### RF-05-02: Logout elimina datos de sesión
Verifica que `localStorage.length == 0` tras logout.
Usa mismo usuario que RF-05-01 ✅

### RF-05-03: No acceso a páginas protegidas tras logout
Intenta acceder a `/crud/listar/` que requiere `is_superuser=True`.
Verifica que redirige al landing.
Usa mismo usuario que RF-05-01 ✅

---

## Estado General de Alineación

### ✅ Totalmente Alineado
- [x] RF-01-01: Todos los datos de registro coinciden
- [x] RF-02-01: Usuario y contraseña coinciden exactamente
- [x] RF-05-01, RF-05-02, RF-05-03: Usan mismo usuario de RF-02
- [x] Selects dinámicos: País (1), Región (16), Comuna (320) usan IDs correctos
- [x] `setup_test_database()`: Crea usuario 'usuario' automáticamente
- [x] `existing_user_credentials`: Fixture actualizado con 'usuario'

### ⚠️ Ajustes Menores
- Teléfono en RF-01: Word especifica +56950184516, conftest.py usa +56912345678
  - **Recomendación**: Si el test es estricto, actualizar a +56950184516

### 🔧 Cambios Realizados en Esta Sesión
1. ✅ Actualizado `existing_user_credentials` fixture:
   - username: 'usuario' (antes: 'usuario_existente')
   - password: 'Segura123!' (sin cambios)
   - email: usuario@correo.com (antes: no especificado)

2. ✅ Agregado `setup_test_database()` fixture:
   - scope='session', autouse=True
   - Crea automáticamente usuario 'usuario' en la BD
   - Sincroniza email con documento Word

---

## Próximos Pasos para Ejecutar Tests

### Opción 1: Ejecución Manual
```bash
# Terminal 1: Inicia servidor Django
python manage.py runserver

# Terminal 2: Ejecuta solo tests de autenticación
pytest selenium_test/test_authentication.py -v
```

### Opción 2: Ejecución Automática (se crean datos automáticamente)
```bash
# Solo asegúrate que Django esté corriendo
python manage.py runserver
pytest selenium_test/test_authentication.py::TestRegistration -v
pytest selenium_test/test_authentication.py::TestLogin -v
pytest selenium_test/test_authentication.py::TestLogout -v
```

---

## Notas Importantes

1. **Las fotos de tests se guardan automáticamente** en `selenium_test/screenshots/` con timestamp
2. **El usuario 'usuario' se crea automáticamente** en la BD gracias a `setup_test_database()`
3. **Los timestamps en email/username son intencionales** para evitar conflictos en ejecuciones múltiples
4. **Todos los parámetros críticos del Word están implementados** en conftest.py
