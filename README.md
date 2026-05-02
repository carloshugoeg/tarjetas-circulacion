# Sistema de Gestion de Tarjetas de Circulacion

Aplicacion cliente-servidor para gestionar tarjetas de circulacion vehicular guatemaltecas. El proyecto usa PostgreSQL, FastAPI y React.

## Stack actual
- Base de datos: PostgreSQL 15
- Backend: Python, FastAPI, SQLAlchemy, Pydantic
- Frontend: React 18, Vite, lucide-react
- Deploy local: Docker Compose

El frontend ya no usa Python, Streamlit ni Flet. No crear `frontend/app.py` ni `frontend/requirements.txt`.

## Estructura
```text
backend/      API REST FastAPI
frontend/     Cliente React + Vite
db_init/      Schema, catalogos y datos de prueba PostgreSQL
```

## Ejecutar
```powershell
docker compose up --build
```

Las imagenes Docker usan las imagenes oficiales de Docker Hub.

Si Docker Desktop esta instalado pero `docker` no aparece en el PATH de PowerShell, usa:
```powershell
.\run_docker.ps1
```

Sin Docker:
```powershell
# Backend
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

URLs:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- PostgreSQL desde el host: `localhost:5433`

## Si Docker falla al descargar imagenes
Antes de revisar el codigo, confirma que Docker Desktop puede descargar cualquier imagen:
```powershell
docker pull hello-world:latest
```

Si falla con `EOF`, `failed to fetch oauth token` o `failed to copy`, el problema esta en Docker Desktop/red/proxy/credenciales, no en este proyecto. Para dejarlo estable:

1. Quita credenciales corruptas de Docker Hub:
```powershell
docker logout
```
2. En Docker Desktop, desactiva "Use containerd for pulling and storing images" si aparece activado.
3. Reinicia Docker y WSL:
```powershell
docker desktop stop
wsl --shutdown
docker desktop start
docker pull hello-world:latest
```
4. Si Docker sigue sin poder descargar imagenes, usa la ruta de rescate con WSL:
```powershell
.\repair_docker_images.ps1
docker compose up --build -d
```

El script usa `skopeo` desde Ubuntu WSL para descargar `postgres:15-alpine`, `python:3.11-slim` y `node:20-alpine`, luego las carga en Docker con `docker load`.

Cuando `docker pull hello-world:latest` funcione, vuelve a correr:
```powershell
docker compose up --build
```

## Verificacion
```powershell
python -m compileall backend
cd frontend
npm run build
npm audit --audit-level=moderate
```
