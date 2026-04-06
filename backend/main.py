from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import Settings
from database import init_db
from routers import documents, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la aplicacion.
    Al arrancar: inicializa la base de datos y precalienta el modelo en RAM
    para que la primera peticion real no tenga que esperar la carga del LLM.
    """
    settings = Settings()
    await init_db(settings)
    await _warm_up_model(settings)
    yield


async def _warm_up_model(settings: Settings) -> None:
    """
    Envia una peticion minima a Ollama para forzar la carga del modelo en RAM.
    Si Ollama no esta listo todavia, lo ignoramos sin lanzar excepcion —
    el modelo se cargara en la primera peticion real del usuario.
    """
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            await client.post(
                settings.ollama_chat_url,
                json={
                    "model": settings.model_name,
                    "messages": [{"role": "user", "content": "ok"}],
                    "stream": False,
                    "options": {"num_predict": 1},
                },
            )
    except Exception:
        pass


app = FastAPI(
    title="Papeleta API",
    description="Analisis privado de documentos oficiales espanoles con Gemma 4.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: permite peticiones desde el frontend de Vite en desarrollo.
# En produccion con un servidor real esto deberia restringirse al dominio propio.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(documents.router)
