import { useState, useEffect } from "react";
import { checkHealth } from "../api.js";

export default function Header() {
  const [modelReady, setModelReady] = useState(null); // null = comprobando

  // Comprobar el estado del modelo al montar el componente
  useEffect(() => {
    checkHealth()
      .then((data) => setModelReady(data.model_ready))
      .catch(() => setModelReady(false));
  }, []);

  return (
    <header style={{
      padding: "1.1rem 1.5rem",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      background: "var(--paper)",
      borderBottom: "1px solid var(--border)",
    }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: "0.7rem" }}>
        <span style={{
          fontFamily: "var(--font-display)",
          fontSize: "1.2rem",
          fontWeight: 500,
          letterSpacing: "-0.02em",
        }}>
          Papeleta
        </span>
        <span style={{ fontSize: "0.72rem", color: "var(--stone)", letterSpacing: "0.02em" }}>
          Documentos oficiales en palabras normales
        </span>
      </div>

      <ModelStatus ready={modelReady} />
    </header>
  );
}

// Indicador visual del estado del modelo
function ModelStatus({ ready }) {
  if (ready === null) {
    return (
      <StatusPill color="var(--stone-light)" dot="#C8C2B6">
        Conectando...
      </StatusPill>
    );
  }
  if (ready) {
    return (
      <StatusPill color="var(--sage)" dot="var(--sage)">
        Modelo listo
      </StatusPill>
    );
  }
  return (
    <StatusPill color="var(--terracotta)" dot="var(--terracotta)">
      Modelo no disponible
    </StatusPill>
  );
}

function StatusPill({ color, dot, children }) {
  return (
    <span style={{
      display: "flex",
      alignItems: "center",
      gap: "0.4rem",
      fontSize: "0.7rem",
      color,
      padding: "0.28rem 0.75rem",
      border: "1px solid var(--border)",
      borderRadius: "var(--radius-full)",
      background: "var(--cream)",
    }}>
      <span style={{
        width: "6px",
        height: "6px",
        borderRadius: "50%",
        background: dot,
        flexShrink: 0,
      }} />
      {children}
    </span>
  );
}
