# Frontend

Cliente React + Vite para el sistema de tarjetas de circulacion.

## Importante
Este frontend reemplaza completamente la interfaz anterior en Python/Streamlit. No usar Streamlit, Flet ni dependencias Python para la UI.

## Archivos principales
- `src/App.jsx`: interfaz, CRUD, mantenimiento y auditoria.
- `src/api.js`: cliente HTTP hacia FastAPI.
- `src/styles.css`: estilos responsivos.
- `package.json`: dependencias y scripts.

## Comandos
```powershell
npm install
npm run dev
npm run build
npm audit --audit-level=moderate
```

La variable `VITE_API_URL` define la API. Valor local recomendado:
```text
VITE_API_URL=http://localhost:8000/api
```
