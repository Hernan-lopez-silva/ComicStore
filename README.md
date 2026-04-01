<<<<<<< HEAD
# Tienda de Comics en Línea

Este proyecto se realizó como parte de la evaluación de la asignatura Desarrollo Web, para la carrera Analista Programador Computacional, Duoc UC.

## Descripción del Proyecto

Comicstore es una aplicación web desarrollada en Django que permite a los usuarios navegar y comprar cómics en línea. El proyecto incluye funcionalidades como:

* **Catálogo de Comics:** Muestra una lista de cómics disponibles con detalles como título, autor, precio e imagen.
* **Carrito de Compras:** Permite a los usuarios agregar cómics al carrito, modificar cantidades y proceder al pago.
* **CRUD de Comics:** Proporciona una interfaz de administración para agregar, editar y eliminar cómics del catálogo.
* **Autenticación y Registro:** Permite a los usuarios crear cuentas, iniciar sesión y gestionar su información personal.
* **Contacto:** Un formulario de contacto para que los usuarios se comuniquen con el administrador de la tienda.

## Despliegue de la aplicación
  
* La aplicación puede ser testeada, con todas sus funcionalidades, en la siguiente dirección:

  * `https://comicstore.up.railway.app/`
  ### Cliente de Prueba
    * Usuario: pablo666 Contraseña: macoy123
  ### Administrador (superuser) de prueba
    * Usuario: admin Contraseña: Oracle.123456 

## Estructura del Proyecto

PruebaDesarrolloWeb3/  
    ├── carrito/  
    ├── comicstore/  
    ├── contacto/  
    ├── crud/  
    ├── home/  
    ├── landing/  
    ├── login/  
    ├── producto/  
    ├── registro/  
    ├── cargar_comics.py  
    ├── cargar_comunas.py  
    ├── cargar_regiones.py  
    ├── comics.csv  
    ├── comunas.csv  
    ├── db.sqlite3  
    ├── manage.py  
    ├── regiones.json  
    └── requirements.txt  

* **`carrito/`, `comicstore/`, `contacto/`, etc.:** Aplicaciones Django que manejan la lógica y vistas de cada sección de la tienda.
* **`cargar_comics.py`, `cargar_comunas.py`, `cargar_regiones.py`:** Scripts para cargar datos iniciales desde archivos CSV y JSON.
* **`comics.csv`, `comunas.csv`:** Archivos de datos que contienen información sobre cómics y comunas.
* **`db.sqlite3`:** Base de datos SQLite que almacena los datos de la aplicación.
* **`manage.py`:** Interfaz de línea de comandos para administrar el proyecto Django.
* **`regiones.json`:** Archivo de datos que contiene información sobre regiones.
* **`requirements.txt`:** Lista de dependencias de Python necesarias para ejecutar el proyecto.

## Instalación y Configuración

1. **Crear entorno virtual:**
   ```bash
   python -m venv nombre-entorno-virtual

2. **Activar entorno virtual:**
   ```bash
    source nombre-entorno-virtual/bin/activate  # En Linux/macOS
    nombre-entorno-virtual\Scripts\activate  # En Windows

3. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Gutierrez-Urrutia/PruebaDesarrolloWeb3.git

4. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt

5. **Ejecutar migraciones:**
   ```bash
   python manage.py migrate

6. **Cargar datos iniciales:**
   ```bash
    python manage.py shell
    >>> exec(open('cargar_comics.py').read())
    >>> exec(open('cargar_comunas.py').read())
    >>> exec(open('cargar_regiones.py').read())

7. **Iniciar el servidor de desarrollo:**
   ```bash
   python manage.py runserver

8. **Creación de superusuario (Admin)**
    ```bash
    python manage.py createsuperuser

# API de Registro de Ubicaciones

Esta API permite poblar los select de país, región y comuna en el formulario de registro del proyecto. A continuación se detallan los endpoints disponibles.

## Endpoints

Los endpoints pueden ser accedidos desde la ruta:

`localhost:8000/registro/`

### Obtener Países

#### `GET /pais`

Devuelve un objeto con el ID del país y el nombre. Actualmente, solo está disponible Chile con ID 1.

**Ejemplo de respuesta:**

```json
{
  "id_pais": 1,
  "nombre_pais": "Chile"
}  
```

### Obtener Regiones por País

#### `GET /region/{id_pais}`

Devuelve todas las regiones correspondientes al país del ID indicado.

**Parámetros:**

* `id_pais` (requerido): El ID del país para el cual se desea obtener las regiones.

**Ejemplo de petición:**

```bash
GET /region/1
```

**Ejemplo de respuesta:**

```json
[
  {
    "id_region": 1,
    "nombre_region": "Región de Arica y Parinacota"
  },
  {
    "id_region": 2,
    "nombre_region": "Región de Tarapacá"
  }
  // ... más regiones
] 
```

### Obtener Comunas por Región

#### `GET /comuna/{id_region}`

Devuelve todas las comunas correspondientes a la región del ID indicado.

**Parámetros:**

* `id_region` (requerido): El ID de la región para la cual se desea obtener las comunas.

**Ejemplo de petición:**

```bash
GET /comuna/1
```

**Ejemplo de respuesta:**

```json
[
  {
    "id_comuna": 1,
    "nombre_comuna": "Arica"
  },
  {
    "id_comuna": 2,
    "nombre_comuna": "Camarones"
  }
  // ... más comunas
]
```

### Notas

* Todos los endpoints deben ser consultados medisnte peticiones `GET`
* Actualmente, la API solo soporta Chile como país disponible.

### Ejemplos de uso en el frontend

```javascript
// Obtener y poblar el select de países
fetch('http://localhost:8000/pais')
  .then(response => response.json())
  .then(data => {
    const paisSelect = document.getElementById('pais');
    const option = document.createElement('option');
    option.value = data.id;
    option.text = data.nombre;
    paisSelect.appendChild(option);
  });

// Obtener y poblar el select de regiones basado en el país seleccionado
document.getElementById('pais').addEventListener('change', function() {
  const paisId = this.value;
  fetch(`http://localhost:8000/region/${paisId}`)
    .then(response => response.json())
    .then(data => {
      const regionSelect = document.getElementById('region');
      regionSelect.innerHTML = ''; // Limpiar opciones previas
      data.forEach(region => {
        const option = document.createElement('option');
        option.value = region.id;
        option.text = region.nombre;
        regionSelect.appendChild(option);
      });
    });
});

// Obtener y poblar el select de comunas basado en la región seleccionada
document.getElementById('region').addEventListener('change', function() {
  const regionId = this.value;
  fetch(`http://localhost:8000/comuna/${regionId}`)
    .then(response => response.json())
    .then(data => {
      const comunaSelect = document.getElementById('comuna');
      comunaSelect.innerHTML = ''; // Limpiar opciones previas
      data.forEach(comuna => {
        const option = document.createElement('option');
        option.value = comuna.id;
        option.text = comuna.nombre;
        comunaSelect.appendChild(option);
      });
    });
});
```
    






















=======
# ComicStore
Proyecto de calidad
>>>>>>> 4459a7b139c407f42fdc4eab2f207f4ac2c77b5a
