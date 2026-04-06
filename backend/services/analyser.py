import json
from datetime import date

import httpx

from config import Settings
from prompts.system import SYSTEM_PROMPT
from services.extractor import image_to_base64


class ModelUnavailableError(Exception):
    pass


class ModelResponseError(Exception):
    pass


async def is_model_ready(settings: Settings) -> bool:
    """
    Comprueba que Ollama esta activo y que el modelo solicitado esta descargado.
    Se usa en el health check y antes de intentar analizar un documento.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(settings.ollama_tags_url)
            resp.raise_for_status()
            models = resp.json().get("models", [])
            return any(
                m["name"].startswith(settings.model_name) for m in models
            )
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


async def analyse_document(
    settings: Settings,
    text: str | None,
    image_bytes: bytes | None,
    template_hint: str = "",
) -> dict:
    """
    Envia el documento a Gemma 4 E4B y parsea la respuesta JSON.

    Acepta texto extraido (PDFs con capa de texto) o imagen en bytes
    (fotos, PDFs escaneados). Nunca los dos a la vez.

    Devuelve el dict con el resultado ya parseado.
    """
    messages = _build_messages(text, image_bytes, template_hint)

    raw_response = await _call_ollama(settings, messages)
    return _parse_json_response(raw_response)


async def analyse_document_stream(
    settings: Settings,
    text: str | None,
    image_bytes: bytes | None,
    template_hint: str = "",
):
    """
    Generador asincrono que emite fragmentos de texto a medida que el modelo
    los produce. El router lo usa para construir una respuesta SSE.
    """
    messages = _build_messages(text, image_bytes, template_hint)

    payload = {
        "model": settings.model_name,
        "messages": messages,
        "stream": True,
        "options": {
            # Temperatura baja para respuestas deterministas con datos oficiales
            "temperature": 0.1,
            "num_predict": 2048,
        },
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream(
            "POST", settings.ollama_chat_url, json=payload
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                data = json.loads(line)
                if data.get("done"):
                    break
                chunk = data.get("message", {}).get("content", "")
                if chunk:
                    yield chunk


def _build_messages(text: str | None, image_bytes: bytes | None, template_hint: str = "") -> list[dict]:
    """
    Construye la lista de mensajes que recibe Ollama.
    El system prompt siempre va primero. El template_hint añade
    instrucciones especificas segun el tipo de documento detectado.
    Inyectamos la fecha actual para que el modelo calcule los plazos correctamente.
    """
    today = date.today().strftime("%d/%m/%Y")

    hint_block = f"\n\nINSTRUCCIONES ADICIONALES:\n{template_hint}" if template_hint else ""
    date_block = f"\n\nFECHA ACTUAL: {today}. Usa esta fecha para calcular los dias restantes de cada plazo."

    user_message: dict = {
        "role": "user",
        "content": (
            f"Analiza este documento oficial y devuelve el JSON solicitado.{date_block}{hint_block}"
            if image_bytes
            else f"Analiza este documento oficial y devuelve el JSON solicitado:{date_block}{hint_block}\n\n{text}"
        ),
    }

    # Adjuntar la imagen en base64 si el documento es visual
    if image_bytes:
        user_message["images"] = [image_to_base64(image_bytes)]

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        user_message,
    ]


async def _call_ollama(settings: Settings, messages: list[dict]) -> str:
    """
    Llama a Ollama en modo no-streaming y devuelve el contenido completo.
    Timeout de 120 segundos para documentos complejos en CPU.
    """
    payload = {
        "model": settings.model_name,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 1024,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.post(settings.ollama_chat_url, json=payload)
            resp.raise_for_status()
    except httpx.ConnectError:
        raise ModelUnavailableError(
            "No se puede conectar con Ollama. "
            "Asegurate de que el servicio esta corriendo."
        )
    except httpx.TimeoutException:
        raise ModelUnavailableError(
            "El modelo tardo demasiado en responder. "
            "Intenta con un documento mas corto."
        )

    return resp.json()["message"]["content"]


def _parse_json_response(raw: str) -> dict:
    """
    Extrae el JSON del texto que devuelve el modelo.
    El modelo puede devolver el JSON rodeado de backticks o con texto previo,
    por eso buscamos el primer '{' y el ultimo '}'.
    """
    start = raw.find("{")
    end = raw.rfind("}") + 1

    if start == -1 or end == 0:
        raise ModelResponseError(
            "El modelo no devolvio un JSON valido. "
            "Intentalo de nuevo o simplifica el documento."
        )

    json_str = raw[start:end]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ModelResponseError(f"Error al parsear la respuesta del modelo: {e}")
