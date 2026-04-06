import { useState, useCallback } from "react";

import Header from "./components/Header.jsx";
import UploadZone from "./components/UploadZone.jsx";
import ProcessingView from "./components/ProcessingView.jsx";
import ResultView from "./components/ResultView.jsx";
import { analyseDocumentStream } from "./api.js";

// Estados posibles de la aplicacion.
// La UI renderiza un componente diferente segun el estado actual.
const STATE = {
  IDLE:       "idle",
  PROCESSING: "processing",
  RESULT:     "result",
  ERROR:      "error",
};

export default function App() {
  const [appState, setAppState]       = useState(STATE.IDLE);
  const [result, setResult]           = useState(null);
  const [errorMsg, setErrorMsg]       = useState("");
  const [streamingText, setStreaming] = useState("");

  const handleFile = useCallback(async (file) => {
    if (!file) return;

    setAppState(STATE.PROCESSING);
    setResult(null);
    setStreaming("");
    setErrorMsg("");

    // Acumulamos los fragmentos del modelo para parsear el JSON al final
    let accumulated = "";

    await analyseDocumentStream(file, {
      onChunk: (chunk) => {
        accumulated += chunk;
        setStreaming(accumulated);
      },
      onDone: () => {
        // El modelo ha terminado: extraemos y parseamos el JSON de la respuesta.
        // Algunos modelos envuelven el JSON en bloques markdown ```json ... ```
        try {
          const start = accumulated.indexOf("{");
          const end   = accumulated.lastIndexOf("}") + 1;
          if (start === -1 || end === 0 || end <= start) {
            throw new Error("Sin JSON en la respuesta");
          }
          const data = JSON.parse(accumulated.slice(start, end));
          setResult(data);
          setAppState(STATE.RESULT);
        } catch {
          setErrorMsg("El modelo no devolvio un JSON valido. Intentalo de nuevo.");
          setAppState(STATE.ERROR);
        }
      },
      onError: (msg) => {
        setErrorMsg(msg || "Ocurrio un error inesperado.");
        setAppState(STATE.ERROR);
      },
    });
  }, []);

  const handleReset = useCallback(() => {
    setAppState(STATE.IDLE);
    setResult(null);
    setErrorMsg("");
  }, []);

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Header />

      <main style={{
        flex: 1,
        maxWidth: "800px",
        width: "100%",
        margin: "0 auto",
        padding: "3rem 1.5rem",
      }}>
        {appState === STATE.IDLE && (
          <UploadZone onFile={handleFile} />
        )}

        {appState === STATE.PROCESSING && (
          <ProcessingView streamingText={streamingText} />
        )}

        {appState === STATE.RESULT && result && (
          <ResultView result={result} onReset={handleReset} />
        )}

        {appState === STATE.ERROR && (
          <ErrorView message={errorMsg} onReset={handleReset} />
        )}
      </main>
    </div>
  );
}

// Componente de error inline (pequeno, no merece fichero propio)
function ErrorView({ message, onReset }) {
  return (
    <div style={{ textAlign: "center", padding: "4rem 0" }}>
      <p style={{
        fontFamily: "var(--font-display)",
        fontSize: "1.4rem",
        fontWeight: 400,
        marginBottom: "0.75rem",
        color: "var(--ink)",
      }}>
        Algo no ha ido bien
      </p>
      <p style={{
        fontSize: "0.9rem",
        color: "var(--stone)",
        marginBottom: "2rem",
        maxWidth: "440px",
        margin: "0 auto 2rem",
      }}>
        {message}
      </p>
      <button
        onClick={onReset}
        style={{
          fontFamily: "var(--font-body)",
          fontSize: "0.85rem",
          color: "var(--stone)",
          background: "none",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-full)",
          padding: "0.5rem 1.25rem",
          cursor: "pointer",
        }}
      >
        Intentar de nuevo
      </button>
    </div>
  );
}
