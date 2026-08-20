import { useState } from 'react';
import { FileUp, LoaderCircle, UploadCloud, Send, FileText } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import { createAssessment } from '../services/api';

const PURPOSES = ['credit_card','debt_consolidation','educational','home_improvement','house','major_purchase','medical','moving','other','renewable_energy','small_business','vacation','wedding'];
const HOMES = ['RENT','MORTGAGE','OWN','NONE','OTHER'];
const CREDIT_FIELDS = ['delinq_2yrs','earliest_cr_line','fico_range_low','fico_range_high','inq_last_6mths','mths_since_last_delinq','mths_since_last_record','open_acc','pub_rec','revol_bal','revol_util','total_acc','acc_now_delinq','tot_coll_amt','tot_cur_bal','mort_acc','pub_rec_bankruptcies','tax_liens'];

function Field({ label, children, hint }) { return <label className="field"><span>{label}</span>{children}{hint && <small>{hint}</small>}</label>; }

export default function NewAssessment({ onAssessment }) {
  const [form, setForm] = useState({ full_name:'', loan_amnt:'', term:'', annual_inc:'', purpose:'', dti:'', installment:'', emp_length:'', home_ownership:'', application_type:'' });
  const [file, setFile] = useState(null); const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  const update = (key, value) => setForm(current => ({ ...current, [key]: value }));
  async function submit(event) { event.preventDefault(); setError(''); if (!file) return setError('Upload the applicant credit report TXT file to continue.'); setBusy(true); try { const result = await createAssessment({ full_name: form.full_name }, form, file); onAssessment(result); } catch (err) { setError(err.message); } finally { setBusy(false); } }
  return <><PageHeader eyebrow="New assessment" title="New loan application" description="Enter your loan details below to see your personalized approval chances" />
    
    <div className="timeline-wrap">
      <div className="timeline-step">
        <div className="timeline-circle">1</div>
      </div>
      <div className="timeline-line"></div>
      <div className="timeline-step">
        <div className="timeline-circle">2</div>
      </div>
      <div className="timeline-line"></div>
      <div className="timeline-step">
        <div className="timeline-circle">3</div>
      </div>
    </div>

    <form className="assessment-form" onSubmit={submit}>
      <section className="form-section"><div className="section-kicker">01 <span>Applicant information</span></div><div className="form-grid two"><Field label="Full name"><input required value={form.full_name} onChange={e => update('full_name', e.target.value)} placeholder="Joann Johnson" /></Field><Field label="Applicant age" hint="For reference only"><input required type="number" min="18" max="100" value={form.age || ''} onChange={e => update('age', e.target.value)} placeholder="32" /></Field></div></section>
      <section className="form-section"><div className="section-kicker">02 <span>Application details</span></div><div className="form-grid three"><Field label="Loan amount"><input required type="number" min="1" value={form.loan_amnt} onChange={e => update('loan_amnt', e.target.value === '' ? '' : Number(e.target.value))} placeholder="15000" /></Field><Field label="Loan term"><select required value={form.term} onChange={e => update('term', e.target.value === '' ? '' : Number(e.target.value))}><option value="" disabled>Select term</option><option value="36">36 months</option><option value="60">60 months</option></select></Field><Field label="Annual income"><input required type="number" min="1" value={form.annual_inc} onChange={e => update('annual_inc', e.target.value === '' ? '' : Number(e.target.value))} placeholder="60000" /></Field><Field label="Monthly installment"><input required type="number" min="0" value={form.installment} onChange={e => update('installment', e.target.value === '' ? '' : Number(e.target.value))} placeholder="500" /></Field><Field label="Debt-to-income ratio"><input required type="number" min="0" max="100" step="0.1" value={form.dti} onChange={e => update('dti', e.target.value === '' ? '' : Number(e.target.value))} placeholder="20" /></Field><Field label="Loan purpose"><select required value={form.purpose} onChange={e => update('purpose', e.target.value)}><option value="" disabled>Select purpose</option>{PURPOSES.map(value => <option key={value}>{value}</option>)}</select></Field><Field label="Employment length"><select required value={form.emp_length} onChange={e => update('emp_length', e.target.value)}><option value="" disabled>Select employment length</option>{['< 1 year',...Array.from({length:9},(_,i)=>`${i+1} years`),'10+ years'].map(value => <option key={value}>{value}</option>)}</select></Field><Field label="Home ownership"><select required value={form.home_ownership} onChange={e => update('home_ownership', e.target.value)}><option value="" disabled>Select ownership</option>{HOMES.map(value => <option key={value}>{value}</option>)}</select></Field><Field label="Application type"><select required value={form.application_type} onChange={e => update('application_type', e.target.value)}><option value="" disabled>Select application type</option><option>Individual</option><option>Joint App</option></select></Field></div></section>
      <section className="form-section"><div className="section-kicker">03 <span>Credit report</span></div><div className="upload-box"><UploadCloud size={26}/><div><strong>Upload Credit Report</strong><p>Use the TXT report with one field per line, such as <code>fico_range_low: 675</code>.</p></div><label className="file-button"><FileUp size={16}/> {file ? file.name : 'Choose TXT file'}<input required type="file" accept=".txt,text/plain" onChange={e => setFile(e.target.files?.[0] || null)} /></label></div><p className="field-note">The report should include the applicant's credit score range, payment and delinquency history, open accounts, credit utilization, and current balances.</p></section>
      <section className="form-section lender-section"><div className="section-kicker">04 <span>Lender information</span></div><div><h3>Predefined for this assessment</h3><p>These standard loan terms are applied automatically to every assessment.</p></div><div className="lender-values"><span>12.5% interest</span><span>Source Verified</span><span>Dec-2015 issue date</span></div></section>
      {error && <div className="error-banner">{error}</div>}
      <div className="form-actions-footer">
        <button type="submit" className="btn-submit" disabled={busy}>
          {busy ? (
            <><LoaderCircle className="spin" size={16} /> Analyzing application...</>
          ) : (
            <><Send size={15} /> Submit Assessment</>
          )}
        </button>
        <button type="button" className="btn-draft" onClick={() => alert('Draft saved (simulated)')}>
          <FileText size={15} /> Save Draft
        </button>
      </div>
    </form></>;
}
