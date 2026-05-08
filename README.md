# Sistema de Gestión de Encomiendas

Proyecto Django para la gestión completa de encomiendas, clientes, empleados, rutas y envíos.

## Características

- Gestión de clientes, empleados y rutas
- Sistema completo de encomiendas con estados y seguimiento
- API REST completa con Django REST Framework
- Autenticación JWT
- Documentación Swagger/OpenAPI
- Interfaz web administrativa
- Soporte Docker

## Tecnologías

- Django 6.0
- Django REST Framework
- PostgreSQL
- Redis (cache)
- Docker & Docker Compose

## Instalación

### Con Docker (Recomendado)

1. Clona el repositorio:
   ```bash
   git clone <url>
   cd mi_proyecto
   ```

2. Construye y ejecuta los contenedores:
   ```bash
   docker-compose up --build
   ```

3. Ejecuta migraciones:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. Crea un superusuario:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

### Sin Docker

1. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configura la base de datos en `config/settings.py`

3. Ejecuta migraciones:
   ```bash
   python manage.py migrate
   ```

4. Crea superusuario:
   ```bash
   python manage.py createsuperuser
   ```

5. Ejecuta el servidor:
   ```bash
   python manage.py runserver
   ```

## Uso

### Interfaz Web

- **Inicio**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

### API REST

- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **OpenAPI Schema**: http://127.0.0.1:8000/api/schema/
- **Redoc**: http://127.0.0.1:8000/api/redoc/

### Endpoints principales

- `GET/POST /api/v1/encomiendas/` - Lista y creación de encomiendas
- `GET/PATCH/DELETE /api/v1/encomiendas/{id}/` - Detalle de encomienda
- `POST /api/v1/encomiendas/{id}/cambiar_estado/` - Cambiar estado
- `GET /api/v1/encomiendas/estadisticas/` - Estadísticas
- `GET /api/v1/clientes/` - Lista de clientes
- `GET /api/v1/rutas/` - Lista de rutas

### Autenticación JWT

1. Obtén tokens:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/v1/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "tu_usuario", "password": "tu_password"}'
   ```

2. Usa el token en requests:
   ```bash
   curl -H "Authorization: Bearer TU_ACCESS_TOKEN" \
     http://127.0.0.1:8000/api/v1/encomiendas/
   ```

## Ejecutar Tests

```bash
python manage.py test api
```

## Estructura del Proyecto

```
mi_proyecto/
├── clientes/          # App de clientes
├── empleados/         # App de empleados (si existe)
├── envios/            # App de encomiendas
├── rutas/             # App de rutas
├── api/               # API REST
├── core/              # Configuración core
├── config/            # Settings y URLs principales
├── static/            # Archivos estáticos
├── templates/         # Templates HTML
├── manage.py
├── requirements.txt
├── docker-compose.yml
└── Dockerfile
```

## Contribución

1. Crea una rama para tu feature
2. Escribe tests
3. Asegura que pasen todos los tests
4. Crea un Pull Request

## Licencia

Este proyecto es para fines educativos.