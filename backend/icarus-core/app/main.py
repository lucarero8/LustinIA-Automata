from fastapi import FastAPI
from app.router import router

app = FastAPI(
    title="Icarus Core",
    version="0.1.0",
    description="Cognitive Core API"
)

app.include_router(router)

@app.get("/")
def root():
    return {"status": "Icarus online"}

