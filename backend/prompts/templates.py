# Instrucciones adicionales que se añaden al system prompt segun el tipo
# de documento detectado por el clasificador.
# Esto mejora la calidad del analisis sin necesidad de fine-tuning.

TEMPLATE_HINTS: dict[str, str] = {
    "Requerimiento Agencia Tributaria": (
        "Presta especial atencion a: el concepto tributario afectado (IRPF, IVA, etc.), "
        "el ejercicio fiscal al que se refiere, el importe reclamado si aparece, "
        "y el plazo exacto para responder. "
        "Si el plazo se expresa en 'dias habiles', indica que los sabados, domingos "
        "y festivos no cuentan."
    ),
    "Notificacion Seguridad Social": (
        "Identifica si es una notificacion de alta, baja, deuda o prestacion. "
        "El numero de afiliacion y el periodo al que se refiere son datos clave. "
        "Si hay un importe de deuda, indicalo claramente."
    ),
    "Multa de trafico": (
        "Extrae OBLIGATORIAMENTE estos datos si aparecen en el documento: "
        "1) Importe total de la sancion en euros (ej: 300,00 EUR). "
        "2) Importe con descuento por pronto pago (ej: 150,00 EUR). "
        "3) Puntos detraidos del permiso de conduccion. "
        "4) Velocidad detectada y limite de la via. "
        "5) Plazo exacto para pagar con descuento (dias naturales). "
        "6) Plazo para presentar alegaciones o recurso. "
        "Incluye los importes exactos en euros en el resumen y en los pasos. "
        "Si el documento indica perdida de puntos, menciona cuantos en los pasos."
    ),
    "Contrato de alquiler": (
        "Resume las condiciones economicas (renta, actualizacion de renta, fianza), "
        "la duracion del contrato y las condiciones de renovacion, "
        "y las obligaciones principales del inquilino y del propietario."
    ),
    "Contrato laboral": (
        "Destaca la categoria profesional, el salario bruto anual, "
        "la duracion del contrato y el periodo de prueba, "
        "y el numero de dias de vacaciones."
    ),
    "Notificacion judicial": (
        "Este tipo de documento es especialmente sensible. "
        "Indica siempre en nota_revision que el usuario consulte con un abogado "
        "antes de actuar. Resume el procedimiento y los plazos con especial cuidado."
    ),
}


def get_template_hint(doc_type: str) -> str:
    """
    Devuelve las instrucciones adicionales para el tipo de documento dado.
    Si no hay plantilla especifica, devuelve una cadena vacia.
    """
    return TEMPLATE_HINTS.get(doc_type, "")
