# 🔧 EcoRetiro

**Sistema de Reciclaje Electrónico** — Plataforma web para gestionar solicitudes de retiro de residuos electrónicos, con panel de operador y dashboard administrativo.

---

## 📋 Stack Tecnológico

### Backend
- **FastAPI** + **SQLAlchemy 2.0** + **PostgreSQL**
- **Alembic** para migraciones
- **JWT** para autenticación
- **Bcrypt** para hash de contraseñas
- **26/26 tests** pasando

### Frontend
- **Vanilla JavaScript** (ES6+)
- **Estética retro Win95/98**
- **Live Server** (desarrollo)
- **GitHub Pages** (producción)

---

## 🚀 Inicio Rápido

### Backend

```bash
cd backend
source entorno/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

El backend estará disponible en `http://127.0.0.1:8000`

### Frontend

```bash
cd frontend
# Abrir en VS Code Live Server o servir con:
python3 -m http.server 5500
```

Accedé a `http://localhost:5500/pages/login.html`

---

## 🔐 Credenciales de Demo

Usuario precargado para testing:

| Email | Password | Rol | Descripción |
|-------|----------|-----|-------------|
| `user1@test.com` | `user1test` | user | Usuario cliente (solicita retiros) |

### Cómo usar:
1. Abrí `https://msanti14.github.io/ecoretiro/`
2. Ingresá el email y password de arriba
3. Explorá las funcionalidades

---

## 📁 Estructura del Proyecto

```
ecoretiro/
├── backend/
│   ├── main.py                 # Aplicación FastAPI
│   ├── models.py               # Modelos SQLAlchemy
│   ├── schemas.py              # Schemas Pydantic
│   ├── database.py             # Conexión BD
│   ├── routers/
│   │   ├── auth.py            # Auth endpoints
│   │   ├── requests.py        # Solicitudes de retiro
│   │   ├── tracking.py        # Rastreo
│   │   ├── profile.py         # Perfil usuario
│   │   ├── operator.py        # Panel operador
│   │   └── admin.py           # Admin dashboard
│   ├── tests/
│   │   └── test_*.py          # Suite de tests
│   ├── alembic/               # Migraciones
│   └── requirements.txt
│
├── frontend/
│   ├── pages/
│   │   ├── login.html         # Login
│   │   ├── profile.html       # Perfil usuario
│   │   ├── request-form.html  # Solicitar retiro
│   │   ├── tracking.html      # Rastreo
│   │   ├── operator.html      # Panel operador
│   │   └── admin.html         # Admin dashboard
│   ├── js/
│   │   ├── api.js             # Fetch wrapper + authFetch
│   │   ├── auth.js            # Lógica autenticación
│   │   └── ui.js              # Utilidades UI
│   ├── css/
│   │   └── retro-modern.css   # Estilos Win95/98
│   └── index.html             # Root
│
└── README.md
```

---

## 🎨 Funcionalidades

### 👤 Cliente
- ✅ Registro e inicio de sesión
- ✅ Solicitar retiro de residuos
- ✅ Ver historial de solicitudes
- ✅ Rastrear estado de retiro
- ✅ Ver perfil y editar datos

### 👨‍💼 Operador
- ✅ Ver solicitudes pendientes
- ✅ Aceptar/rechazar solicitudes
- ✅ Registrar retiro completado
- ✅ Ver historial de operaciones

### 🛡️ Administrador
- ✅ Acceso a todo (cliente + operador)
- ✅ Dashboard con estadísticas
- ✅ Gestión de usuarios
- ✅ Reportes y métricas

---

## 🧪 Testing

```bash
cd backend
source entorno/bin/activate
pytest
```

**26 tests** en la suite de autenticación, solicitudes, rastreo y admin.

---

## 🔗 API Endpoints

### Auth
- `POST /auth/login` — Iniciar sesión
- `POST /auth/register` — Registrarse

### Solicitudes
- `GET /requests` — Listar solicitudes (filtrado por rol)
- `POST /requests` — Crear solicitud de retiro
- `GET /requests/{id}` — Detalle de solicitud
- `PATCH /requests/{id}/status` — Actualizar estado

### Tracking
- `GET /tracking/{request_id}` — Estado del retiro

### Operador
- `GET /operator/pending` — Solicitudes pendientes
- `PATCH /operator/requests/{id}/accept` — Aceptar solicitud

### Admin
- `GET /admin/stats` — Estadísticas
- `GET /admin/users` — Listar usuarios
- `GET /admin/reports` — Reportes

---

## 🛠️ Desarrollo

### Agregar migración (después de cambiar modelos)

```bash
cd backend
source entorno/bin/activate
alembic revision --autogenerate -m "Descripción del cambio"
alembic upgrade head
```

### Variables de entorno

Crear `.env` en `backend/`:
```
DATABASE_URL=postgresql://user:password@localhost/ecoretiro
SECRET_KEY=tu-clave-secreta-aqui
```

---

## 📝 Notas de Seguridad

- ✅ **Hashing**: Contraseñas hasheadas con bcrypt (no reversible)
- ✅ **CORS**: Configurado para desarrollo local
- ✅ **JWT**: Tokens con expiración
- ✅ **HTML Escape**: Validación en frontend para prevenir XSS
- ⚠️ **HTTPS**: Usar en producción

---

## 🚢 Deploy

### GitHub Pages (Frontend)
- Pushear `frontend/` a rama `gh-pages`
- Accesible en `https://msanti14.github.io/ecoretiro/frontend/`

### Railway / Render (Backend)
- Conectar repo → seleccionar rama main
- Configurar PostgreSQL add-on
- Deploy automático en cada push

---

## 👤 Autor

**Santiago** ([@msanti14](https://github.com/msanti14)) — Desarrollador full-stack, Ushuaia, Argentina

---

## 📄 Licencia

MIT

