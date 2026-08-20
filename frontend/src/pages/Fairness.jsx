import { useEffect, useState } from 'react';
import { AlertTriangle, RefreshCw, ShieldCheck } from 'lucide-react';
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import PageHeader from '../components/PageHeader';
import { fetchFairness } from '../services/api';

const percent = value => `${(value * 100).toFixed(1)}%`;
const tooltipFormatter = value => [percent(value), 'Rate'];

export default function Fairness() {
	const [metrics, setMetrics] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState('');

	useEffect(() => {
		let active = true;
		async function loadMetrics() {
			try {
				const data = await fetchFairness();
				const formattedData = Array.isArray(data)
					? data.map(row => ({
						state_group: row.state_group,
						accuracy: parseFloat(row.accuracy),
						selection_rate: parseFloat(row.selection_rate),
						false_positive_rate: parseFloat(row.false_positive_rate),
						false_negative_rate: parseFloat(row.false_negative_rate),
						precision: parseFloat(row.precision),
						recall: parseFloat(row.recall)
					}))
					: [];
				if (active) setMetrics(formattedData);
			} catch (requestError) {
				if (active) setError(requestError.message);
			} finally {
				if (active) setLoading(false);
			}
		}
		loadMetrics();
		return () => { active = false; };
	}, []);

	const selectionMetrics = [...metrics].sort((left, right) => right.selection_rate - left.selection_rate);

	return <>
		<PageHeader eyebrow="Responsible AI" title="Fairness analysis" description="Compare model outcomes across state groups and monitor disparity in error rates." />
		{loading && <section className="panel fairness-status"><ShieldCheck size={22} /><span>Loading fairness metrics...</span></section>}
		{!loading && error && <section className="panel fairness-status fairness-error"><AlertTriangle size={22} /><div><strong>Unable to load metrics</strong><p>{error}</p><button type="button" onClick={() => window.location.reload()}><RefreshCw size={15} /> Retry</button></div></section>}
		{!loading && !error && !metrics.length && <section className="panel fairness-status"><ShieldCheck size={22} /><span>No fairness metrics are available.</span></section>}
		{!loading && !error && metrics.length > 0 && <div className="fairness-grid">
			<section className="panel chart-panel">
				<div className="panel-heading"><div><p className="eyebrow">Error rates</p><h2>False outcomes by state</h2></div><span className="chart-note">Lower is better</span></div>
				<div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><BarChart data={metrics} margin={{ top: 12, right: 8, left: 0, bottom: 4 }}>
					<CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5eaf1" />
					<XAxis
					  dataKey="state_group"
					  angle={-90}
					  textAnchor="end"
					  interval={0}
					  height={120}
					  tick={{ fontSize: 10, dy: 8 }}
					  tickLine={false}
					  axisLine={false}
					/>
					<YAxis
					  tickFormatter={(tick) => `${Math.round(Number(tick) * 100)}%`}
					  domain={[0, 'auto']}
					  tickLine={false}
					  axisLine={false}
					  width={50}
					/>
					<Tooltip formatter={tooltipFormatter} contentStyle={{ borderRadius: 8, border: '1px solid #e5eaf1' }} />
					<Legend />
					<Bar dataKey="false_positive_rate" name="False positive" fill="#d95d4c" radius={[4, 4, 0, 0]} />
					<Bar dataKey="false_negative_rate" name="False negative" fill="#2864d7" radius={[4, 4, 0, 0]} />
				</BarChart></ResponsiveContainer></div>
			</section>
			<section className="panel chart-panel">
				<div className="panel-heading"><div><p className="eyebrow">Selection rate</p><h2>Approval selection by state</h2></div><span className="chart-note">Descending</span></div>
				<div className="chart-wrap chart-wrap-vertical"><ResponsiveContainer width="100%" height={860}><BarChart data={selectionMetrics} layout="vertical" margin={{ top: 4, right: 16, left: 4, bottom: 4 }}>
					<CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e5eaf1" />
					<XAxis type="number" domain={[0, 'auto']} tickFormatter={(tick) => `${(tick * 100).toFixed(0)}%`} axisLine={false} tickLine={false} />
					<YAxis type="category" dataKey="state_group" axisLine={false} tickLine={false} width={38} interval={0} />
					<Tooltip formatter={tooltipFormatter} contentStyle={{ borderRadius: 8, border: '1px solid #e5eaf1' }} />
					<Bar dataKey="selection_rate" name="Selection rate" fill="#258866" radius={[0, 4, 4, 0]} />
				</BarChart></ResponsiveContainer></div>
			</section>
		</div>}
	</>;
}
