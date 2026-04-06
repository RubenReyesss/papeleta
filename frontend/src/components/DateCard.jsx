// Componente para mostrar una fecha limite con su nivel de urgencia.
// Urgente = menos de 15 dias o ya vencida.

export default function DateCard({ fecha }) {
  const urgente = fecha.urgente || fecha.dias < 0;

  const bg     = urgente ? "var(--terracotta-light)" : "var(--sage-light)";
  const border = urgente ? "var(--terracotta-border)" : "var(--sage-border)";
  const badge  = urgente ? "var(--terracotta)"        : "var(--sage)";

  const badgeText = fecha.dias < 0
    ? `Vencio hace ${Math.abs(fecha.dias)} dias`
    : fecha.dias === 0
    ? "Vence hoy"
    : `${fecha.dias} dias`;

  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      gap: "1rem",
      padding: "0.75rem 1rem",
      borderRadius: "var(--radius-sm)",
      border: `1px solid ${border}`,
      background: bg,
    }}>
      <span style={{ fontSize: "0.88rem", color: "var(--ink)", lineHeight: 1.4 }}>
        {fecha.label}
      </span>

      <span style={{
        fontSize: "0.75rem",
        fontWeight: 500,
        padding: "0.25rem 0.75rem",
        borderRadius: "var(--radius-full)",
        background: badge,
        color: "white",
        whiteSpace: "nowrap",
        flexShrink: 0,
      }}>
        {badgeText}
      </span>
    </div>
  );
}
