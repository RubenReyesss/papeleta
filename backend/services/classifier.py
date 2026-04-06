from dataclasses import dataclass

# Mapa de tipo de documento a palabras clave que lo identifican.
# El clasificador recorre esta lista en orden y devuelve el primer match.
# Los tipos mas especificos deben ir antes que los genericos.
DOCUMENT_PATTERNS: list[tuple[str, list[str]]] = [
    (
        "Requerimiento Agencia Tributaria",
        ["agencia tributaria", "aeat", "irpf", "iva", "impuesto sobre la renta",
         "declaracion de la renta", "hacienda", "inspeccion fiscal",
         "requerimiento de informacion", "liquidacion provisional"],
    ),
    (
        "Notificacion Seguridad Social",
        ["tesoreria general", "seguridad social", "cotizacion", "alta laboral",
         "baja laboral", "prestacion por desempleo", "sepe", "inem",
         "pension", "incapacidad temporal"],
    ),
    (
        "Multa de trafico",
        ["direccion general de trafico", "dgt", "infraccion de trafico",
         "velocidad", "semaforo en rojo", "aparcamiento", "boletín de denuncia",
         "multa", "sancion de trafico", "expediente sancionador de trafico"],
    ),
    (
        "Notificacion de ayuntamiento",
        ["ayuntamiento", "municipio", "policia municipal", "ibi",
         "impuesto sobre bienes inmuebles", "padron municipal",
         "licencia de obras", "tasa municipal"],
    ),
    (
        "Contrato de alquiler",
        ["contrato de arrendamiento", "arrendatario", "arrendador",
         "renta mensual", "fianza", "ley de arrendamientos urbanos", "lau",
         "alquiler", "inquilino", "propietario"],
    ),
    (
        "Contrato laboral",
        ["contrato de trabajo", "empresa", "trabajador", "salario",
         "jornada laboral", "convenio colectivo", "estatuto de los trabajadores",
         "periodo de prueba", "categoria profesional"],
    ),
    (
        "Notificacion judicial",
        ["juzgado", "tribunal", "demanda", "sentencia", "auto",
         "providencia", "diligencia", "secretario judicial",
         "letrado de la administracion de justicia", "proceso judicial"],
    ),
    (
        "Comunicacion bancaria",
        ["entidad bancaria", "hipoteca", "prestamo", "tipo de interes",
         "euribor", "cuota mensual", "banco", "caja", "iban",
         "comision", "extracto"],
    ),
    (
        "Documento oficial",
        # Categoria generica para todo lo que no encaje en las anteriores
        [],
    ),
]


@dataclass
class ClassificationResult:
    doc_type: str
    # Puntuacion de confianza: cuantas palabras clave se han encontrado
    score: int


def classify_document(text: str) -> ClassificationResult:
    """
    Identifica el tipo de documento buscando palabras clave en el texto.
    Devuelve el tipo con mayor puntuacion.

    Esta clasificacion rapida se usa para elegir el prompt mas adecuado
    antes de llamar al modelo. No es exhaustiva: el modelo puede corregirla.
    """
    text_lower = text.lower()
    best_type  = "Documento oficial"
    best_score = 0

    for doc_type, keywords in DOCUMENT_PATTERNS:
        # Si no hay palabras clave, es la categoria generica (ultimo recurso)
        if not keywords:
            continue

        score = sum(1 for kw in keywords if kw in text_lower)

        if score > best_score:
            best_score = score
            best_type  = doc_type

    return ClassificationResult(doc_type=best_type, score=best_score)
