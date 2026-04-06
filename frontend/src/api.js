// URL base de la API. Vite proxea /api al backend en desarrollo.
const API_BASE = "/api";

/**
 * Comprueba si el modelo esta listo antes de intentar un analisis.
 * El componente Header lo llama al montar para mostrar el estado.
 */
export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("No se pudo conectar con el servidor");
  return res.json();
}

/**
 * Sube un fichero y devuelve el resultado del analisis completo.
 * Usar cuando no se necesita streaming (mas sencillo de manejar).
 *
 * @param {File} file
 * @returns {Promise<object>} resultado con tipo, resumen, pasos y fechas
 */
export async function analyseDocument(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/documents/analyse`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Error desconocido" }));
    throw new Error(err.detail || `Error ${res.status}`);
  }

  return res.json();
}

/**
 * Version streaming del analisis. Llama al callback onChunk con cada
 * fragmento de texto que el modelo va generando, y a onDone al terminar.
 *
 * Usa ReadableStream para leer el SSE sin librerias externas.
 *
 * @param {File} file
 * @param {{ onChunk: (text: string) => void, onDone: () => void, onError: (msg: string) => void }} callbacks
 */
export async function analyseDocumentStream(file, { onChunk, onDone, onError }) {
  const form = new FormData();
  form.append("file", file);

  let res;
  try {
    res = await fetch(`${API_BASE}/documents/analyse/stream`, {
      method: "POST",
      body: form,
    });
  } catch {
    onError("No se pudo conectar con el servidor.");
    return;
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Error desconocido" }));
    onError(err.detail || `Error ${res.status}`);
    return;
  }

  // Leer el stream linea a linea (formato SSE: "data: {...}\n\n")
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop(); // La ultima linea puede estar incompleta

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const payload = line.slice(6).trim();
      if (!payload) continue;

      try {
        const event = JSON.parse(payload);
        if (event.error) {
          onError(event.error);
          return;
        }
        if (event.done) {
          onDone();
          return;
        }
        if (event.chunk) {
          onChunk(event.chunk);
        }
      } catch {
        // Fragmento SSE malformado, ignorar
      }
    }
  }

  onDone();
}
