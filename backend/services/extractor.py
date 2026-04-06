import base64
import io

import pdfplumber
from PIL import Image

# Tipos MIME aceptados por el endpoint de subida
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
}

# Limite conservador de tokens para no saturar el contexto del modelo.
# 1 token aprox = 3 caracteres en espanol.
MAX_TEXT_CHARS = 80_000

# Lado maximo de imagen en pixeles antes de reducirla.
# 1600px es suficiente para que el modelo lea texto sin problemas.
MAX_IMAGE_DIMENSION = 1600


class UnsupportedFileTypeError(Exception):
    pass


class FileTooLargeError(Exception):
    pass


def validate_upload(content: bytes, content_type: str, max_bytes: int) -> None:
    """
    Lanza una excepcion si el fichero no cumple los requisitos basicos.
    Se llama antes de cualquier procesamiento para fallar rapido.
    """
    if len(content) > max_bytes:
        raise FileTooLargeError(
            f"El fichero pesa {len(content) // 1024 // 1024}MB. "
            f"El maximo permitido es {max_bytes // 1024 // 1024}MB."
        )
    if content_type not in ALLOWED_MIME_TYPES:
        raise UnsupportedFileTypeError(
            f"Tipo de fichero no soportado: {content_type}. "
            f"Tipos aceptados: PDF, JPG, PNG, WEBP."
        )


def extract_from_pdf(pdf_bytes: bytes) -> tuple[str | None, bytes | None]:
    """
    Intenta extraer texto de un PDF.

    Devuelve una tupla (texto, imagen):
    - Si el PDF tiene capa de texto: (texto_extraido, None)
    - Si el PDF es un escaneo sin texto: (None, imagen_de_la_primera_pagina)

    Usar el texto directo es mucho mas rapido y preciso que enviar una imagen,
    especialmente en documentos de Hacienda con tablas y numeros.
    """
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        pages_text = []
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                pages_text.append(text.strip())

    full_text = "\n\n--- Pagina siguiente ---\n\n".join(pages_text)

    # Si hay texto suficiente, lo usamos directamente sin pasar por vision
    if len(full_text.strip()) > 100:
        return _truncate_text(full_text), None

    # PDF escaneado: convertir la primera pagina a imagen para que el modelo la vea
    try:
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(pdf_bytes, dpi=200, first_page=1, last_page=1)
        image_bytes = _image_to_bytes(images[0])
        return None, image_bytes
    except Exception:
        # Si pdf2image falla (poppler no instalado, etc.), devolver lo que tenemos
        return full_text or "[No se pudo extraer texto del PDF]", None


def normalize_image(image_bytes: bytes) -> bytes:
    """
    Redimensiona la imagen si es demasiado grande y la convierte a JPEG.
    Esto reduce el numero de tokens visuales y acelera la inferencia.
    """
    img = Image.open(io.BytesIO(image_bytes))

    # Convertir modos no estandar (RGBA, paleta, etc.) a RGB
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    # Reducir si supera el maximo, manteniendo la proporcion
    if max(img.size) > MAX_IMAGE_DIMENSION:
        img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.LANCZOS)

    return _image_to_bytes(img)


def image_to_base64(image_bytes: bytes) -> str:
    """Codifica los bytes de una imagen en base64 para enviarla a Ollama."""
    return base64.b64encode(image_bytes).decode("utf-8")


def _image_to_bytes(img: Image.Image) -> bytes:
    """Convierte un objeto PIL Image a bytes JPEG."""
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def _truncate_text(text: str) -> str:
    """
    Recorta el texto si supera el limite de caracteres para el modelo.
    Anade una nota al final para que el modelo sepa que hay mas contenido.
    """
    if len(text) <= MAX_TEXT_CHARS:
        return text

    truncated = text[:MAX_TEXT_CHARS]
    return truncated + (
        "\n\n[NOTA: El documento es muy largo. "
        "Solo se muestra la primera parte. "
        "Si hay informacion importante mas adelante, indicalo en nota_revision.]"
    )
