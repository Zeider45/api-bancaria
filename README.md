# API Bancaria (SIB Bridge)

Proyecto fullstack con:

- **Backend**: Django + django-ninja
- **Async**: Celery + Redis (worker + beat)
- **DB**: Postgres (por defecto en Docker)
- **Frontend**: Next.js

## Requisitos

- Docker + Docker Compose
- Node.js (solo si quieres correr frontend fuera de Docker)

> Recomendación: para desarrollo y para producción “rápida” use Docker Compose.

---

## Variables de entorno

Este proyecto se configura **solo** por archivos `.env`.

- Usa `.env.example` para desarrollo.
- Usa `.env.prod.example` como base para producción.

> Nota: `docker-compose.yml` usa `env_file: .env`, así que necesitas un archivo `.env` en la raíz para levantar los contenedores.

### SSL entre Frontend y Backend (opcional)

La comunicación **Frontend ↔ Backend** puede ser por HTTP o HTTPS según tu despliegue:

- En **desarrollo local** normalmente usas HTTP:
  - `NEXT_PUBLIC_API_URL=http://localhost:8000`
  - `INTERNAL_API_URL=http://backend:8000`
  - `DJANGO_FORCE_SSL=false`

- En **producción** lo recomendado es HTTPS hacia el usuario (browser) y HTTP interno entre contenedores _detrás de un reverse proxy_:
  - `NEXT_PUBLIC_API_URL=https://api.midominio.com` (browser → proxy → backend)
  - `INTERNAL_API_URL=http://backend:8000` (solo dentro de la red docker)

`DJANGO_FORCE_SSL` solo debe ponerse en `true` cuando realmente tienes terminación TLS (Nginx/Ingress) y este envía `X-Forwarded-Proto: https`.
Si no tienes TLS terminada delante del backend, deja `DJANGO_FORCE_SSL=false` para evitar redirecciones a `https://`.

### Backend (Django)

Variables comunes:

- `DJANGO_SETTINGS_MODULE`:
  - Desarrollo: `config.settings.development`
  - Producción: `config.settings.produccion`
- `DJANGO_SECRET_KEY` (obligatorio en producción)
- `ALLOWED_HOSTS` (producción), ejemplo: `api.midominio.com,backend`

Base de datos (si no usas `DATABASE_URL`):

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`

O usando URL:

- `DATABASE_URL` (ej: `postgresql://user:pass@host:5432/dbname` o `sqlite:///./db.sqlite3`)

Redis/Celery:

- `REDIS_URL` (ej: `redis://redis:6379/0`)
- `CELERY_TASK_ALWAYS_EAGER` (opcional dev): `true` para ejecutar tasks en el mismo proceso (sin worker)

SUDEBAN (según ambiente):

- `SUDEBAN_API_URL`
- `SUDEBAN_USERNAME`
- `SUDEBAN_PASSWORD`
- `SUDEBAN_WEBHOOK_URL` (y opcionales `SUDEBAN_WEBHOOK_URL_API01..API04`)
- `SUDEBAN_ID_ENTIDAD_BANCARIA`
- `SUDEBAN_REQUIRE_HTTPS` (recomendado `true` en prod)

### Frontend (Next.js)

En `docker-compose.yml`:

- `NEXT_PUBLIC_API_URL` (URL pública del backend para el browser)
- `INTERNAL_API_URL` (URL interna del backend desde el contenedor)
- `NEXTAUTH_URL`
- `NEXTAUTH_SECRET` (obligatorio en producción)

---

## Levantar en Development (Docker)

Desde la raíz del repo:

1. Crea tu `.env`:

```powershell
Copy-Item .env.example .env
```

2. Levanta el stack:

```bash
docker compose up --build
```

Servicios:

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Postgres: localhost:5432
- Redis: localhost:6379

Celery:

- `celery_worker` corre el worker
- `celery_beat` corre los schedules (beat)

---

## Levantar en Development (sin Celery/Redis)

Si quieres desarrollar sin levantar worker/redis, puedes ejecutar Celery en modo “eager” (tareas síncronas).

Edita tu `.env` y setea:

- `CELERY_TASK_ALWAYS_EAGER=true`

Luego levanta normalmente:

```bash
docker compose up --build
```

> Nota: esto es útil para desarrollo, pero no refleja el comportamiento real de colas.

---

## Levantar en Producción (Docker Compose)

Este repo incluye settings de producción en `config.settings.produccion`.
La forma más simple de levantar “modo producción” con Compose es usar un `.env` con secretos reales.

### 1) Crea tu `.env` de producción

```powershell
Copy-Item .env.prod.example .env
notepad .env
```

Completa al menos:

- `DJANGO_SECRET_KEY`
- `ALLOWED_HOSTS`
- `POSTGRES_PASSWORD` (y `DATABASE_URL` consistente)
- `SUDEBAN_USERNAME` / `SUDEBAN_PASSWORD`
- `SUDEBAN_WEBHOOK_URL` (HTTPS)
- `NEXTAUTH_URL` / `NEXTAUTH_SECRET`

### 2) Levanta el stack

```bash
docker compose up --build -d
```

### 3) HTTPS / Reverse proxy (recomendado)

En producción, Django debe ir detrás de un reverse proxy (Nginx/Ingress) que termine TLS.

- Asegura que el proxy setee `X-Forwarded-Proto: https`.
- Publica solo los puertos necesarios.

---

## Notas de Celery (importante)

- La configuración vive en:
  - `backend/config/celery.py`
  - `backend/config/settings/base.py`
  - overrides en `backend/config/settings/development.py` y `backend/config/settings/produccion.py`

- Celery Beat incluye schedules para:
  - Intervención (API-01): cada hora
  - Subasta (API-02): cada minuto + reintentos cada 10 min
  - Mesa de cambio (API-04): cada hora

---

## Troubleshooting

- **Los contenedores levantan pero Django no conecta a DB**: revisa `DATABASE_URL` y que `postgres` esté healthy.
- **Celery no ejecuta tareas**: verifica logs de `celery_beat` y que `redis` esté arriba.
- **CORS / llamadas desde el frontend**: revisa `NEXT_PUBLIC_API_URL` y `CORS_ALLOWED_ORIGINS`.

---

## Comandos útiles

- Ver logs de celery:
  - `docker compose logs -f celery_worker`
  - `docker compose logs -f celery_beat`

- Reiniciar servicios:
  - `docker compose restart backend celery_worker celery_beat`
