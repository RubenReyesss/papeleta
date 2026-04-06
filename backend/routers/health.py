from fastapi import APIRouter, Depends

from config import Settings
from schemas import HealthResponse
from services.analyser import is_model_ready

router = APIRouter(prefix="/api", tags=["system"])


def get_settings() -> Settings:
    return Settings()


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """
    Comprueba si el sistema esta listo para analizar documentos.
    El frontend llama a este endpoint al cargar para mostrar el estado.
    """
    model_ready = await is_model_ready(settings)

    return HealthResponse(
        status="ok" if model_ready else "degraded",
        model_ready=model_ready,
        model_name=settings.model_name,
    )
