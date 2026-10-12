export function Alert({ alert, onClose }) {
  if (!alert) return null;
  return (
    <div className={`alert ${alert.type}`} role="alert">
      <span>{alert.text}</span>
      <button className="link" onClick={onClose} aria-label="Dismiss">×</button>
    </div>
  );
}

export function StatCard({ label, value, tone }) {
  return (
    <div className={`stat ${tone || ""}`}>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

export function StatusBadge({ status }) {
  return <span className={`badge ${status}`}>{status}</span>;
}

export function Empty({ text }) {
  return <p className="empty">{text}</p>;
}
