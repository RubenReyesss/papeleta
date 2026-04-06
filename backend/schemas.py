from pydantic import BaseModel
from typing import Literal


class DateAlert(BaseModel):
    """Una fecha limite extraida del documento."""

    label: str
    # Dias restantes desde hoy. Negativo si ya ha pasado el plazo.
    dias: int
    urgente: bool


class AnalysisResult(BaseModel):
    """
    Resultado completo del analisis de un documento.
    Este es el objeto que devuelve el endpoint y que muestra el frontend.
    """

    # Tipo de documento identificado (Hacienda, contrato, multa, etc.)
    tipo: str

    # Nivel de confianza del modelo en su propio analisis
    confianza: Literal["alta", "media", "baja"]

    # Resumen en lenguaje llano de que dice el documento
    resumen: str

    # Lista ordenada de acciones que debe tomar el usuario
    pasos: list[str]

    # Fechas y plazos importantes detectados en el documento
    fechas: list[DateAlert]

    # Si el modelo no esta seguro de algo, lo indica aqui.
    # El frontend muestra este aviso destacado si no es None.
    nota_revision: str | None = None


class HealthResponse(BaseModel):
    """Estado del sistema devuelto por el endpoint de health check."""

    status: Literal["ok", "degraded"]
    # True si Ollama responde y el modelo esta disponible
    model_ready: bool
    model_name: str


class ErrorResponse(BaseModel):
    """Formato estandar para errores de la API."""

    code: str
    message: str
