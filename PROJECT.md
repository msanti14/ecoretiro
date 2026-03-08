# PROJECT.md — EcoRetiro

## Descripción

**EcoRetiro** es una plataforma web para la gestión de retiro, clasificación y
reciclaje de residuos electrónicos (e-waste). Permite a ciudadanos, instituciones
y empresas solicitar el retiro de aparatos en desuso, trackear el proceso y conocer
el destino final del material: reutilizado, reacondicionado o reciclado.

- **Inspiración:** Cybercirujas (Buenos Aires)
- **Contexto inicial:** Ushuaia, Tierra del Fuego, Argentina
- **Escalabilidad:** Adoptable por otros municipios u operadores

---

## Tipos de Usuario

| Tipo | Descripción |
|------|-------------|
| Ciudadano común | Cables, impresoras, monitores, PCs, celulares |
| Usuario consciente | Sabe que el e-waste contamina |
| Institución educativa | Upgrades masivos de equipamiento |
| Empresa / Organismo | Equipamiento obsoleto en volumen |
| Junta vecinal | Puntos de acopio comunitario |
| ONG / Municipio | Campañas de recolección |

---

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | Python 3.12 + FastAPI |
| ORM | SQLAlchemy + Alembic |
| Base de datos | PostgreSQL |
| Auth | JWT (python-jose + passlib) |
| Fotos | Cloudinary |
| Frontend | HTML5 + CSS3 + JS vanilla + Tailwind CSS |
| Mapas | Leaflet.js |
| Testing | pytest + httpx |
| Entorno | venv + pyenv (Debian 10 Buster) |

---

## Alcance del MVP

**Incluido:**
- Registro y login de usuarios
- Formulario de solicitud con fotos, dirección, fecha y franja horaria
- Generación automática de número de seguimiento
- Tracking público del estado
- Panel de operadores (cambio de estados)
- Dashboard de estadísticas para admin

**Fuera del MVP:**
- App móvil (Flutter o React Native)
- Geolocalización del vehículo en tiempo real
- Clasificación automática con IA (visión artificial)
- Módulo de reacondicionamiento de PCs
- Notificaciones por email / WhatsApp
- QR de confirmación + firma digital

---

## Vehículos Disponibles

| Vehículo | Uso |
|----------|-----|
| AUTO | Retiros pequeños y medianos |
| DUCATO | Retiros grandes o múltiples equipos |

---

## Roles

| Rol | Descripción |
|-----|-------------|
| USER | Ciudadano que genera solicitudes |
| OPERATOR | Gestiona retiros y cambia estados |
| ADMIN | Acceso total + dashboard + usuarios |

---

## Recordatorios de Entorno

```bash
source entorno/bin/activate          # activar entorno virtual
pip install -r requirements.txt      # instalar dependencias
pip freeze > requirements.txt        # guardar nuevas dependencias
uvicorn backend.main:app --reload    # servidor de desarrollo
pytest tests/ -v                     # correr tests
# http://localhost:8000/docs         # documentación automática API
```
