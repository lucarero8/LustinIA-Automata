# Contenido recomendado para backend/icarus-core/app/main.py

from fastapi import FastAPI
from app.router import router as api_router

# Define tu aplicación principal una sola vez con todos sus metadatos
app = FastAPI(
    title="ICARUS AI Core",
    version="0.1.0",
    description="Cognitive Core API"
)

# Incluye el router en el prefijo '/api' para organizar todas tus rutas nuevas
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    # Una ruta raíz simple para verificar que el servicio base está online
    return {"status": "Icarus online"}
