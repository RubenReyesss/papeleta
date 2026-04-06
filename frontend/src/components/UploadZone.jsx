import { useState, useRef, useCallback } from "react";

// Tipos de fichero que acepta el input (debe coincidir con el backend)
const ACCEPTED_TYPES = ".pdf,image/jpeg,image/png,image/webp";

export default function UploadZone({ onFile }) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) onFile(file);
  }, [onFile]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleChange = useCallback((e) => {
    const file = e.target.files?.[0];
    if (file) onFile(file);
  }, [onFile]);

  // Pegar desde el portapapeles (util en escritorio)
  const handlePaste = useCallback((e) => {
    const items = Array.from(e.clipboardData?.items || []);
    const imageItem = items.find((item) => item.type.startsWith("image/"));
    if (imageItem) {
      const file = imageItem.getAsFile();
      if (file) onFile(file);
    }
  }, [onFile]);

  return (
    <div onPaste={handlePaste}>
      <h1 style={{
        fontFamily: "var(--font-display)",
        fontSize: "clamp(1.8rem, 5vw, 2.6rem)",
        fontWeight: 400,
        lineHeight: 1.15,
        letterSpacing: "-0.03em",
        marginBottom: "0.75rem",
      }}>
        Entiende lo que te{" "}
        <em style={{ fontStyle: "italic", color: "var(--terracotta)" }}>piden</em>{" "}
        de verdad
      </h1>

      <p style={{
        fontSize: "1rem",
        color: "var(--stone)",
        marginBottom: "2.5rem",
        lineHeight: 1.65,
        maxWidth: "540px",
      }}>
        Sube cualquier carta oficial, notificacion o contrato
        y te explicamos en palabras normales que significa y que tienes que hacer.
      </p>

      {/* Zona de arrastre principal */}
      <div
        role="button"
        tabIndex={0}
        aria-label="Zona de subida de documentos. Arrastra un fichero o haz clic para seleccionar."
        onDragOver={handleDragOver}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
        style={{
          border: `1.5px dashed ${dragOver ? "var(--terracotta)" : "var(--border-dark)"}`,
          borderRadius: "var(--radius-lg)",
          background: dragOver ? "var(--terracotta-light)" : "var(--paper)",
          padding: "3.5rem 2rem",
          textAlign: "center",
          cursor: "pointer",
          transition: "border-color 0.2s, background 0.2s",
          outline: "none",
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_TYPES}
          onChange={handleChange}
          style={{ display: "none" }}
          aria-hidden="true"
        />

        {/* Icono de subida */}
        <UploadIcon />

        <p style={{
          fontFamily: "var(--font-display)",
          fontSize: "1.1rem",
          fontWeight: 400,
          marginTop: "1rem",
          marginBottom: "0.35rem",
        }}>
          Arrastra aqui tu documento
        </p>
        <p style={{ fontSize: "0.8rem", color: "var(--stone)" }}>
          o haz clic para seleccionar &mdash; tambien puedes pegar con Ctrl+V
        </p>
      </div>

      {/* Formatos soportados */}
      <div style={{
        display: "flex",
        gap: "0.5rem",
        justifyContent: "center",
        marginTop: "1.25rem",
        flexWrap: "wrap",
      }}>
        {["PDF", "JPG", "PNG", "Foto de movil"].map((label) => (
          <span key={label} style={{
            fontSize: "0.7rem",
            color: "var(--stone)",
            padding: "0.28rem 0.75rem",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-full)",
            background: "var(--paper)",
          }}>
            {label}
          </span>
        ))}
      </div>

      {/* Aviso de privacidad */}
      <p style={{
        textAlign: "center",
        fontSize: "0.72rem",
        color: "var(--stone-light)",
        marginTop: "1rem",
      }}>
        El analisis se realiza en tu propio ordenador. Ningun documento sale de tu red.
      </p>
    </div>
  );
}

function UploadIcon() {
  return (
    <svg
      width="44"
      height="44"
      viewBox="0 0 44 44"
      fill="none"
      style={{ margin: "0 auto", display: "block" }}
    >
      <rect x="1" y="1" width="42" height="42" rx="10" stroke="var(--border-dark)" strokeWidth="1" fill="var(--cream)" />
      <path d="M22 28V18M22 18L17 23M22 18L27 23" stroke="var(--stone)" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M14 32h16" stroke="var(--border-dark)" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  );
}
