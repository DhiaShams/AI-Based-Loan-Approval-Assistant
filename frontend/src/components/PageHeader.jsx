export default function PageHeader({ eyebrow, title, description, action }) {
  return <header className="page-header"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1>{description && <p className="page-description">{description}</p>}</div>{action}</header>;
}

export function Metric({ label, value, tone = '' }) { return <div className={`metric-card ${tone}`}><span>{label}</span><strong>{value}</strong></div>; }

export function EmptyState({ message = 'No assessment is available. Please run a new assessment first.' }) { return <div className="empty-state"><span>◎</span><p>{message}</p></div>; }
