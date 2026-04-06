import { useState } from "react";
import DateCard from "./DateCard.jsx";

// Muestra el resultado completo del analisis en tres secciones:
// resumen, pasos a seguir y fechas importantes.
export default function ResultView({ result, onReset }) {
  return (
    <div>
      <ResultHeader result={result} />

      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {/* Seccion 1: resumen en lenguaje llano */}
        <ResultCard
          label="En pocas palabras"
          copyText={result.resumen}
          animationDelay="0s"
        >
          <p style={{ fontSize: "0.95rem", lineHeight: 1.7, color: "#2C2826" }}>
            {result.resumen}
          </p>
        </ResultCard>

        {/* Seccion 2: pasos concretos que debe dar el usuario */}
        <ResultCard
          label="Lo que tienes que hacer"
          copyText={result.pasos.map((p, i) => `${i + 1}. ${p}`).join("\n")}
          animationDelay="0.1s"
        >
          <ol style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "0.7rem" }}>
            {result.pasos.map((paso, i) => (
              <li key={i} style={{ display: "flex", gap: "0.75rem", alignItems: "flex-start" }}>
                <span style={{
                  width: "22px",
                  height: "22px",
                  borderRadius: "50%",
                  background: "var(--ink)",
                  color: "var(--cream)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "0.65rem",
                  fontWeight: 500,
                  flexShrink: 0,
                  marginTop: "2px",
                }}>
                  {i + 1}
                </span>
                <span style={{ fontSize: "0.9rem", lineHeight: 1.55, color: "#2C2826" }}>
                  {paso}
                </span>
              </li>
            ))}
          </ol>
        </ResultCard>

        {/* Seccion 3: fechas y plazos (solo si hay alguno) */}
        {result.fechas?.length > 0 && (
          <ResultCard
            label="Fechas que no puedes olvidar"
            animationDelay="0.2s"
          >
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {result.fechas.map((fecha, i) => (
                <DateCard key={i} fecha={fecha} />
              ))}
            </div>
          </ResultCard>
        )}

        {/* Aviso del modelo si no esta seguro de algo */}
        {result.nota_revision && (
          <NoteRevision nota={result.nota_revision} />
        )}
      </div>

      <button
        onClick={onReset}
        style={{
          display: "block",
          marginTop: "2.5rem",
          fontFamily: "var(--font-body)",
          fontSize: "0.8rem",
          color: "var(--stone)",
          background: "none",
          border: "none",
          cursor: "pointer",
          textDecoration: "underline",
          textUnderlineOffset: "3px",
          padding: 0,
        }}
      >
        Analizar otro documento
      </button>
    </div>
  );
}

// Cabecera del resultado con el tipo de documento y nivel de confianza
function ResultHeader({ result }) {
  const confianzaColor = {
    alta:  "var(--sage)",
    media: "#8A7340",
    baja:  "var(--terracotta)",
  }[result.confianza] ?? "var(--stone)";

  return (
    <div style={{ marginBottom: "2rem", animation: "fade-up 0.4s ease forwards" }}>
      <span style={{
        display: "inline-block",
        fontSize: "0.7rem",
        letterSpacing: "0.06em",
        textTransform: "uppercase",
        color: "var(--terracotta)",
        background: "var(--terracotta-light)",
        border: "1px solid var(--terracotta-border)",
        borderRadius: "var(--radius-full)",
        padding: "0.28rem 0.85rem",
        marginBottom: "0.8rem",
      }}>
        {result.tipo}
      </span>

      <h2 style={{
        fontFamily: "var(--font-display)",
        fontSize: "clamp(1.4rem, 4vw, 1.9rem)",
        fontWeight: 400,
        letterSpacing: "-0.025em",
        lineHeight: 1.2,
        marginBottom: "0.4rem",
      }}>
        Aqui tienes lo que necesitas saber
      </h2>

      <p style={{ fontSize: "0.78rem", color: confianzaColor }}>
        Confianza del analisis: {result.confianza}
      </p>
    </div>
  );
}

// Tarjeta contenedora con boton de copiar
function ResultCard({ label, copyText, animationDelay = "0s", children }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!copyText) return;
    navigator.clipboard.writeText(copyText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    });
  };

  return (
    <div style={{
      background: "var(--paper)",
      border: "1px solid var(--border)",
      borderRadius: "var(--radius-md)",
      padding: "1.4rem 1.5rem",
      animation: "fade-up 0.45s ease forwards",
      animationDelay,
      opacity: 0,
    }}>
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: "1rem",
      }}>
        <span style={{
          fontSize: "0.68rem",
          letterSpacing: "0.07em",
          textTransform: "uppercase",
          color: "var(--stone)",
        }}>
          {label}
        </span>

        {copyText && (
          <button
            onClick={handleCopy}
            style={{
              fontFamily: "var(--font-body)",
              fontSize: "0.68rem",
              color: copied ? "var(--sage)" : "var(--stone)",
              background: "none",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-sm)",
              padding: "0.2rem 0.6rem",
              cursor: "pointer",
              transition: "color 0.15s, border-color 0.15s",
            }}
          >
            {copied ? "Copiado" : "Copiar"}
          </button>
        )}
      </div>

      {children}
    </div>
  );
}

// Aviso destacado cuando el modelo indica que algo debe revisarse
function NoteRevision({ nota }) {
  return (
    <div style={{
      padding: "1rem 1.25rem",
      borderRadius: "var(--radius-md)",
      border: "1px solid #E8D8A0",
      background: "#FDFBF0",
      animation: "fade-up 0.45s ease 0.3s forwards",
      opacity: 0,
    }}>
      <p style={{
        fontSize: "0.68rem",
        letterSpacing: "0.07em",
        textTransform: "uppercase",
        color: "#8A7340",
        marginBottom: "0.5rem",
      }}>
        Revisa con un profesional
      </p>
      <p style={{ fontSize: "0.88rem", color: "#2C2826", lineHeight: 1.6 }}>
        {nota}
      </p>
    </div>
  );
}
