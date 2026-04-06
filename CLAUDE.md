# Papeleta — Guia del proyecto

## Que hace este proyecto

Aplicacion web que recibe documentos oficiales espanoles (PDF, foto de papel,
carta escaneada) y devuelve tres cosas en lenguaje llano:
- Un resumen de que dice el documento
- Los pasos concretos que debe dar el usuario
- Las fechas limite relevantes con indicador de urgencia

El analisis lo realiza Gemma 4 E4B corriendo localmente via Ollama.
Ningun documento sale de la red del usuario.

## Reglas de codigo

- Sin emojis en ningun fichero de codigo o documentacion tecnica.
- Comentarios en espanol explicando el "por que", no el "que".
- Nombres de variables y funciones en ingles, en snake_case.
- Clases en PascalCase. Tipos anotados en todas las funciones.
- Un fichero, una responsabilidad. No mezclar logica con routing.
- Nunca hardcodear valores que puedan cambiar: todo va a config.py o .env.

## Estructura del proyecto

```
papeleta/
├── start.ps1               <- Arranca backend y frontend con un comando
├── .env.example            <- Plantilla de variables de entorno
├── CLAUDE.md               <- Este fichero
│
├── skills/                 <- Guias para el asistente de IA
│   ├── backend.md
│   ├── gemma.md
│   ├── document_processing.md
│   └── prompts.md
│
├── backend/                <- API FastAPI
│   ├── requirements.txt
│   ├── main.py             <- Punto de entrada, middlewares
│   ├── config.py           <- Settings tipados desde .env
│   ├── schemas.py          <- Modelos Pydantic de entrada/salida
│   ├── database.py         <- Historial en SQLite (aiosqlite)
│   │
│   ├── services/
│   │   ├── extractor.py    <- OCR y extraccion de texto
│   │   ├── classifier.py   <- Detecta el tipo de documento
│   │   └── analyser.py     <- Llama a Ollama y parsea JSON
│   │
│   ├── prompts/
│   │   ├── system.py       <- System prompt principal
│   │   └── templates.py    <- Hints por tipo de documento
│   │
│   └── routers/
│       ├── documents.py    <- POST /api/documents/analyse
│       └── health.py       <- GET /api/health
│
└── frontend/               <- React + Vite
    ├── vite.config.js      <- Proxy /api al backend en desarrollo
    ├── src/
    │   ├── App.jsx         <- Maquina de estados (idle/processing/result)
    │   ├── api.js          <- Todas las llamadas al backend
    │   └── components/
    │       ├── Header.jsx
    │       ├── UploadZone.jsx
    │       ├── ProcessingView.jsx
    │       ├── ResultView.jsx
    │       └── DateCard.jsx
    └── styles/
        └── global.css
```

## Como arrancar (primera vez)

```powershell
# 1. Instalar Ollama para Windows desde https://ollama.com/download/windows

# 2. Descargar el modelo (solo una vez, ~10 GB)
ollama pull gemma4:e4b

# 3. Copiar variables de entorno
cp .env.example .env

# 4. Arrancar backend y frontend
.\start.ps1

# 5. Abrir en el navegador
http://localhost:5173
```

## Como arrancar (despues de la primera vez)

Asegurate de que Ollama esta corriendo (icono en la bandeja del sistema) y ejecuta:

```powershell
.\start.ps1
```

## Endpoints de la API

| Metodo | Ruta                         | Descripcion                          |
|--------|------------------------------|--------------------------------------|
| GET    | /api/health                  | Estado del modelo                    |
| POST   | /api/documents/analyse       | Analisis completo (espera el JSON)   |
| POST   | /api/documents/analyse/stream| Analisis con streaming SSE           |

## Anadir un nuevo tipo de documento

1. Añadir palabras clave en `backend/services/classifier.py`
2. Añadir instrucciones especificas en `backend/prompts/templates.py`
3. Ver `skills/prompts.md` para guia detallada

## Variables de entorno

| Variable      | Default                    | Descripcion                          |
|---------------|----------------------------|--------------------------------------|
| OLLAMA_HOST   | http://localhost:11434     | URL de Ollama                        |
| MODEL_NAME    | gemma4:e4b                 | Nombre del modelo en Ollama          |
| DB_PATH       | ./history.db               | Ruta del SQLite                      |
| MAX_FILE_MB   | 20                         | Tamano maximo de fichero subido      |

## Skills disponibles

- `skills/backend.md` — estructura FastAPI y convenios del proyecto
- `skills/gemma.md` — como llamar a Ollama, parametros, streaming
- `skills/document_processing.md` — pipeline de extraccion de texto
- `skills/prompts.md` — como escribir y modificar prompts
