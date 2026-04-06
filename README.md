# Papeleta

Analiza documentos oficiales espanoles (cartas de Hacienda, contratos, multas de trafico...)
y explica en lenguaje normal que dice el documento y que tienes que hacer.

**Todo el procesamiento ocurre en tu propio ordenador. Ningun documento sale de tu red.**

---

## Como funciona

1. Subes un PDF o una foto del documento
2. El backend extrae el texto (o lo lee como imagen si es un escaneo)
3. Gemma 4 E4B analiza el contenido localmente via Ollama
4. Recibes un resumen claro, los pasos a seguir y las fechas limite con urgencia

Tipos de documento reconocidos: multas de trafico, requerimientos de Hacienda, contratos laborales, contratos de alquiler, notificaciones judiciales, comunicaciones bancarias y mas.

---

## Requisitos

- Windows 10/11 con 16 GB de RAM
- [Python 3.11+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [Ollama para Windows](https://ollama.com/download/windows)
- Conexion a internet solo para la primera descarga del modelo (~10 GB)

---

## Puesta en marcha (primera vez)

**Paso 1** — Instalar [Ollama para Windows](https://ollama.com/download/windows) y descargar el modelo:

```powershell
ollama pull gemma4:e4b
```

La descarga es de unos 10 GB y solo se hace una vez.

**Paso 2** — Copiar las variables de entorno:

```powershell
cp .env.example .env
```

No hace falta cambiar nada para un uso local estandar.

**Paso 3** — Arrancar la aplicacion:

```powershell
.\start.ps1
```

La primera vez instala las dependencias automaticamente. Las siguientes arranca directamente.

**Paso 4** — Abrir en el navegador:

```
http://localhost:5173
```

El indicador en la cabecera muestra si el modelo esta listo.

---

## Uso diario

Asegurate de que Ollama esta corriendo (icono en la bandeja del sistema) y ejecuta:

```powershell
.\start.ps1
```

---

## Formatos soportados

| Formato             | Como se procesa                              |
|---------------------|----------------------------------------------|
| PDF con texto       | Extraccion directa (mas rapido y preciso)    |
| PDF escaneado       | El modelo lee la imagen de la primera pagina |
| JPG / PNG / WEBP    | El modelo lee la imagen directamente         |
| Foto de movil       | El modelo lee la imagen directamente         |

Limite de tamano: 20 MB por fichero (configurable en `.env`).

---

## Velocidad de analisis

| Hardware                | Tiempo aproximado |
|-------------------------|-------------------|
| CPU sin GPU (16 GB RAM) | 1 - 3 minutos     |
| GPU NVIDIA (8 GB VRAM)  | 5 - 15 segundos   |
| Apple Silicon (M1/M2/M3)| 10 - 30 segundos  |

Los PDFs con capa de texto son notablemente mas rapidos que las imagenes.

---

## Estructura del proyecto

```
papeleta/
├── backend/
│   ├── main.py             Punto de entrada FastAPI
│   ├── config.py           Variables de entorno tipadas
│   ├── schemas.py          Modelos Pydantic
│   ├── database.py         Historial en SQLite
│   ├── services/
│   │   ├── extractor.py    Extraccion de texto e imagenes
│   │   ├── classifier.py   Deteccion del tipo de documento
│   │   └── analyser.py     Llamadas a Ollama y parseo JSON
│   ├── prompts/
│   │   ├── system.py       System prompt principal
│   │   └── templates.py    Instrucciones por tipo de documento
│   └── routers/
│       ├── documents.py    POST /api/documents/analyse
│       └── health.py       GET /api/health
│
├── frontend/
│   └── src/
│       ├── App.jsx         Maquina de estados de la UI
│       ├── api.js          Llamadas al backend
│       └── components/     Header, UploadZone, ResultView...
│
├── .env.example            Variables de entorno (plantilla)
├── start.ps1               Arranca backend y frontend
└── CLAUDE.md               Guia tecnica del proyecto
```

---

## Variables de entorno

| Variable      | Por defecto                | Descripcion                        |
|---------------|----------------------------|------------------------------------|
| OLLAMA_HOST   | http://localhost:11434     | URL del servidor Ollama            |
| MODEL_NAME    | gemma4:e4b                 | Modelo a usar                      |
| DB_PATH       | ./history.db               | Ruta del fichero SQLite            |
| MAX_FILE_MB   | 20                         | Tamano maximo de fichero en MB     |

---

## API

| Metodo | Ruta                            | Descripcion                          |
|--------|---------------------------------|--------------------------------------|
| GET    | /api/health                     | Estado del modelo                    |
| POST   | /api/documents/analyse          | Analisis completo (respuesta directa)|
| POST   | /api/documents/analyse/stream   | Analisis con streaming SSE           |

---

## Problemas frecuentes

**El indicador del modelo aparece en rojo**
Ollama no esta corriendo o el modelo no esta descargado.
Abre Ollama desde la bandeja del sistema y, si es necesario, ejecuta `ollama pull gemma4:e4b`.

**La respuesta tarda mucho**
Sin GPU el modelo puede tardar 1-3 minutos, especialmente con imagenes.
Usa PDFs con capa de texto para analisis mas rapidos.

**Error "file too large"**
El limite por defecto es 20 MB. Puedes cambiarlo con `MAX_FILE_MB` en `.env`.

**El backend no arranca**
Comprueba que Python 3.11+ esta instalado y que el entorno virtual se creo correctamente
en `backend/.venv/`. Si algo falla, borra la carpeta `.venv` y ejecuta `.\start.ps1` de nuevo.

---

## Licencia

MIT — consulta el fichero [LICENSE](LICENSE) para mas detalles.
