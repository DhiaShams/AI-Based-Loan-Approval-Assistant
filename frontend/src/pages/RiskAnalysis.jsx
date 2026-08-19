import { Link } from 'react-router-dom';
import { ArrowUpRight, CircleAlert, Sparkles } from 'lucide-react';
import PageHeader, { EmptyState, Metric } from '../components/PageHeader';

export default function RiskAnalysis({ assessment }) {
  if (!assessment) return <><PageHeader eyebrow="Risk analysis" title="Current applicant" /><EmptyState /></>;
  const { applicant, prediction, decision } = assessment;
  const level = decision.risk_level.toLowerCase();
  return <><PageHeader eyebrow="Risk analysis" title="Assessment result" description="A clear view of the model prediction and the operational decision policy." action={<Link className="secondary-button" to="/decision-explanation"><Sparkles size={16}/> View explanation</Link>} />
    <div className="applicant-banner"><div className="person-badge">{applicant.name.slice(0,1).toUpperCase()}</div><div><span>Applicant</span><strong>{applicant.name}</strong></div><div className={`status-pill ${level}`}>{decision.risk_level} risk</div></div>
    <div className="metrics-grid six"><Metric label="Prediction" value={prediction.class.toUpperCase()} /><Metric label="Default risk" value={`${prediction.default_probability_percent.toFixed(2)}%`} tone="risk" /><Metric label="Non-default" value={`${prediction.non_default_probability_percent.toFixed(2)}%`} tone="positive" /><Metric label="Risk level" value={decision.risk_level} tone={level} /><Metric label="Recommendation" value={decision.recommendation} /><Metric label="Assessment ID" value={assessment.id.replace('assessment-', '#')} /></div>
    <section className="panel probability-panel"><div className="panel-heading"><div><p className="eyebrow">Probability split</p><h2>How the risk is distributed</h2></div><CircleAlert size={20}/></div><Probability label="Default risk" value={prediction.default_probability_percent} tone="risk"/><Probability label="Non-default probability" value={prediction.non_default_probability_percent} tone="positive"/></section>
    <div className="notice"><ArrowUpRight size={18}/><span>The recommendation is based on the estimated default probability and the configured decision policy.</span></div>
  </>;
}
function Probability({ label, value, tone }) { return <div className="probability-row"><div><span>{label}</span><strong>{value.toFixed(2)}%</strong></div><div className="track"><i className={tone} style={{width:`${value}%`}}/></div></div>; }
