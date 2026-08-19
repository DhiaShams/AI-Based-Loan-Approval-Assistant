import { useEffect, useState } from 'react';
import { NavLink, Navigate, Route, Routes, useNavigate } from 'react-router-dom';
import { BarChart3, FileText, LayoutDashboard, Plus, Scale, Sparkles } from 'lucide-react';
import { fetchApplications } from './services/api';
import Dashboard from './pages/Dashboard';
import NewAssessment from './pages/NewAssessment';
import RiskAnalysis from './pages/RiskAnalysis';
import DecisionExplanation from './pages/DecisionExplanation';
import Applications from './pages/Applications';
import Fairness from './pages/Fairness';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/new-assessment', label: 'New assessment', icon: Plus },
  { to: '/applications', label: 'Applications', icon: FileText },
  { to: '/risk-analysis', label: 'Risk analysis', icon: BarChart3 },
  { to: '/decision-explanation', label: 'Decision explanation', icon: Sparkles },
  { to: '/fairness', label: 'Fairness', icon: Scale },
];

export default function App() {
  const [assessment, setAssessment] = useState(null);
  const [history, setHistory] = useState([]);
  const navigate = useNavigate();

  useEffect(() => { fetchApplications().then(items => { setHistory(items); if (items[0]) setAssessment(items[0]); }).catch(() => {}); }, []);

  function onAssessment(result) {
    setAssessment(result);
    setHistory(current => [result, ...current.filter(item => item.id !== result.id)]);
    navigate('/risk-analysis');
  }

  function selectAssessment(result) { setAssessment(result); navigate('/risk-analysis'); }

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark">L</div><div><strong>LOAN AI</strong><span>DECISION INTELLIGENCE</span></div></div>
      <nav>{navItems.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} end={to === '/'}><Icon size={17} /><span>{label}</span></NavLink>)}</nav>
      <div className="sidebar-footer"><div className="avatar">AJ</div><div><strong>Alex Johnson</strong><span>Senior Loan Officer</span></div></div>
    </aside>
    <main className="main-content"><Routes>
      <Route path="/" element={<Dashboard history={history} />} />
      <Route path="/new-assessment" element={<NewAssessment onAssessment={onAssessment} />} />
      <Route path="/risk-analysis" element={<RiskAnalysis assessment={assessment} />} />
      <Route path="/decision-explanation" element={<DecisionExplanation assessment={assessment} />} />
      <Route path="/applications" element={<Applications history={history} onSelect={selectAssessment} />} />
      <Route path="/fairness" element={<Fairness />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes></main>
  </div>;
}
