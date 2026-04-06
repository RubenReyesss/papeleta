import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from config import Settings
from database import save_analysis
from prompts.templates import get_template_hint
from schemas import AnalysisResult, ErrorResponse
from services.analyser import (
    ModelUnavailableError,
    ModelResponseError,
    analyse_document,
    analyse_document_stream,
    is_model_ready,
)
from services.classifier import classify_document
from services.extractor import (
    FileTooLargeError,
    UnsupportedFileTypeError,
    extract_from_pdf,
    normalize_image,
    validate_upload,
)

# Hint para imagenes: el clasificador trabaja con texto, no con pixeles,
# asi que para imagenes enviamos instrucciones genericas al modelo para que
# extraiga todos los datos numericos y economicos que encuentre.
_IMAGE_HINT = (
    "Extrae TODOS los datos numericos y economicos del documento: "
    "importes exactos en euros, fechas, plazos en dias, puntos, porcentajes. "
    "Si es una multa: importe total, importe con descuento, puntos detraidos, velocidad detectada y limite. "
    "Si es un contrato laboral: salario bruto anual exacto, categoria profesional, periodo de prueba. "
    "Si es un requerimiento de Hacienda: importe reclamado, concepto, ejercicio fiscal. "
    "Incluye siempre los importes exactos en euros dentro del resumen y de los pasos."
)

router = APIRouter(prefix="/api/documents", tags=["documents"])


def get_settings() -> Settings:
    return Settings()


@router.post(
    "/analyse",
    response_model=AnalysisResult,
    responses={
        415: {"model": ErrorResponse, "description": "Tipo de fichero no soportado"},
        413: {"model": ErrorResponse, "description": "Fichero demasiado grande"},
        503: {"model": ErrorResponse, "description": "Modelo no disponible"},
    },
)
async def analyse_document_endpoint(
    file: UploadFile,
    settings: Settings = Depends(get_settings),
) -> AnalysisResult:
    """
    Endpoint sincrono. Recibe un fichero y devuelve el resultado completo de una vez.
    Util cuando no se necesita streaming (integraciones, tests, etc.).
    Para la demo interactiva usar /analyse/stream.
    """
    content = await file.read()
    content_type = file.content_type or ""

    # Validar tamano y tipo antes de cualquier procesamiento costoso
    try:
        validate_upload(content, content_type, settings.max_file_bytes)
    except FileTooLargeError as e:
        raise HTTPException(status_code=413, detail=str(e))
    except UnsupportedFileTypeError as e:
        raise HTTPException(status_code=415, detail=str(e))

    if not await is_model_ready(settings):
        raise HTTPException(
            status_code=503,
            detail="El modelo no esta disponible. Ejecuta: ollama pull gemma4:e4b",
        )

    text, image_bytes = _extract_content(content, content_type)
    template_hint = get_template_hint(classify_document(text).doc_type) if text else _IMAGE_HINT

    try:
        result = await analyse_document(settings, text, image_bytes, template_hint)
    except ModelUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ModelResponseError as e:
        raise HTTPException(status_code=422, detail=str(e))

    await save_analysis(settings, file.filename or "documento", result)
    return AnalysisResult(**result)


@router.post("/analyse/stream")
async def analyse_document_stream_endpoint(
    file: UploadFile,
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    """
    Endpoint streaming (SSE). Emite fragmentos del JSON a medida que el modelo
    los genera, permitiendo que el frontend muestre progreso en tiempo real.
    """
    content = await file.read()
    content_type = file.content_type or ""

    try:
        validate_upload(content, content_type, settings.max_file_bytes)
    except FileTooLargeError as e:
        raise HTTPException(status_code=413, detail=str(e))
    except UnsupportedFileTypeError as e:
        raise HTTPException(status_code=415, detail=str(e))

    if not await is_model_ready(settings):
        raise HTTPException(status_code=503, detail="El modelo no esta disponible.")

    text, image_bytes = _extract_content(content, content_type)
    template_hint = get_template_hint(classify_document(text).doc_type) if text else _IMAGE_HINT

    async def event_stream():
        full_response = []
        try:
            async for chunk in analyse_document_stream(settings, text, image_bytes, template_hint):
                full_response.append(chunk)
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            # Guardamos el resultado en historial al terminar el stream
            raw = "".join(full_response)
            await save_analysis(settings, file.filename or "documento", {"raw": raw})
            yield f"data: {json.dumps({'done': True})}\n\n"

        except (ModelUnavailableError, ModelResponseError) as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            # Impedir que proxies intermedios almacenen en buffer el stream
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _extract_content(
    content: bytes, content_type: str
) -> tuple[str | None, bytes | None]:
    """
    Decide como procesar el fichero segun su tipo MIME.
    Devuelve (texto, None) para PDFs con capa de texto,
    o (None, imagen) para imagenes y PDFs escaneados.
    """
    if content_type == "application/pdf":
        return extract_from_pdf(content)
    return None, normalize_image(content)
