import { useState, useEffect } from "react";

const STEPS = [
  "Leyendo el documento",
  "Identificando el tipo de escrito",
  "Analizando el contenido con Gemma 4",
  "Extrayendo fechas y plazos",
];

// Cada paso aparece con un pequeno retraso para dar sensacion de progreso real
const STEP_DELAY_MS = 900;

export default function ProcessingView({ streamingText = "" }) {
  const [visible, setVisible] = useState([]);

  useEffect(() => {
    const timers = STEPS.map((_, i) =>
      setTimeout(() => {
        setVisible((prev) => [...prev, i]);
      }, i * STEP_DELAY_MS)
    );
    return () => timers.forEach(clearTimeout);
  }, []);

  // El paso activo es el ultimo que se ha hecho visible
  const activeStep = visible.length - 1;

  return (
    <div style={{ paddingTop: "1rem" }}>
      <h2 style={{
        fontFamily: "var(--font-display)",
        fontSize: "1.6rem",
        fontWeight: 400,
        letterSpacing: "-0.02em",
        marginBottom: "0.4rem",
      }}>
        Analizando tu documento
      </h2>
      <p style={{ fontSize: "0.85rem", color: "var(--stone)", marginBottom: "2.5rem" }}>
        Esto puede tardar entre 1 y 3 minutos segun el equipo
      </p>

      {streamingText && (
        <div style={{
          marginBottom: "2rem",
          padding: "1rem 1.2rem",
          background: "var(--paper)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-md)",
          fontFamily: "monospace",
          fontSize: "0.72rem",
          color: "var(--stone)",
          whiteSpace: "pre-wrap",
          wordBreak: "break-all",
          maxHeight: "120px",
          overflowY: "hidden",
          // Mostramos solo el final del texto para que parezca que va escribiendo
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-end",
        }}>
          {streamingText.slice(-400)}
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "0" }}>
        {STEPS.map((step, i) => {
          const isVisible = visible.includes(i);
          const isDone    = isVisible && i < activeStep;
          const isActive  = isVisible && i === activeStep;

          return (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "1rem",
                padding: "0.9rem 1.1rem",
                borderRadius: "var(--radius-md)",
                border: "1px solid",
                borderColor: isDone ? "var(--border)" : isActive ? "var(--terracotta-border)" : "transparent",
                background: isDone ? "var(--paper)" : isActive ? "var(--terracotta-light)" : "transparent",
                opacity: isVisible ? 1 : 0,
                transform: isVisible ? "translateY(0)" : "translateY(8px)",
                transition: "opacity 0.4s ease, transform 0.4s ease, background 0.2s",
                marginBottom: "0.4rem",
              }}
            >
              <StepMarker done={isDone} active={isActive} index={i} />
              <span style={{
                fontSize: "0.9rem",
                color: isVisible ? "var(--ink)" : "var(--stone-light)",
              }}>
                {step}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function StepMarker({ done, active, index }) {
  const bg = done ? "var(--sage)" : active ? "var(--terracotta)" : "var(--border)";
  const color = done || active ? "white" : "var(--stone)";

  return (
    <div style={{
      width: "28px",
      height: "28px",
      borderRadius: "50%",
      background: bg,
      color,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      flexShrink: 0,
      fontSize: "0.7rem",
      fontWeight: 500,
      transition: "background 0.3s",
    }}>
      {done ? <CheckIcon /> : active ? <Spinner /> : index + 1}
    </div>
  );
}

function CheckIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
      <path d="M2 7L5 10L11 4" stroke="white" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function Spinner() {
  return (
    <div style={{
      width: "13px",
      height: "13px",
      border: "1.8px solid rgba(255,255,255,0.35)",
      borderTopColor: "white",
      borderRadius: "50%",
      animation: "spin 0.7s linear infinite",
    }} />
  );
}
