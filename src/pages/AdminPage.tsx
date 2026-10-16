import { FormEvent, useEffect, useState } from 'react';
import { Activity, ArrowDownToLine, ClipboardList, Download, FileText, LogOut, RefreshCw, Search, ShieldCheck, Users } from 'lucide-react';
import { apiRequest, getCsrf } from '../api';

type Enquiry = { id: number; kind: 'contact' | 'quote'; name: string; company: string; email: string; phone: string; requirement: string; message: string; status: string; internal_note: string; created_at: string; attachment_id?: number | null; location?: string };
type Dashboard = { total_enquiries: number; new_enquiries: number; quote_requests: number; open_requests: number; closed_requests: number };
const statusOptions = ['New', 'Contacted', 'In Progress', 'Quoted', 'Won', 'Closed'];

export default function AdminPage() {
  const [csrf, setCsrf] = useState(''); const [authenticated, setAuthenticated] = useState(false); const [username, setUsername] = useState(''); const [password, setPassword] = useState(''); const [loginBusy, setLoginBusy] = useState(false); const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  const [dashboard, setDashboard] = useState<Dashboard | null>(null); const [enquiries, setEnquiries] = useState<Enquiry[]>([]); const [query, setQuery] = useState(''); const [statusFilter, setStatusFilter] = useState('All'); const [typeFilter, setTypeFilter] = useState('All'); const [dateFrom, setDateFrom] = useState(''); const [dateTo, setDateTo] = useState(''); const [selected, setSelected] = useState<Enquiry | null>(null); const [saving, setSaving] = useState(false); const [toast, setToast] = useState('');
  useEffect(() => { getCsrf().then(v => setCsrf(v.csrfToken)).catch(() => setCsrf('')); }, []);
  const loadDashboard = async () => {
    setBusy(true); setError('');
    try { const [d, items] = await Promise.all([apiRequest<Dashboard>('/admin/dashboard/'), apiRequest<Enquiry[]>('/admin/enquiries/')]); setDashboard(d); setEnquiries(items); setAuthenticated(true); }
    catch (err) { setError(err instanceof Error ? err.message : 'Unable to load admin data.'); if (authenticated) setAuthenticated(false); }
    finally { setBusy(false); }
  };
  useEffect(() => { if (authenticated) void loadDashboard(); // load when login succeeds
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authenticated]);
  const login = async (e: FormEvent) => {
    e.preventDefault(); setLoginBusy(true); setError('');
    try {
      let token = csrf; if (!token) { const value = await getCsrf(); token = value.csrfToken; setCsrf(token); }
      const session = await apiRequest<{ csrfToken: string }>('/auth/login/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': token }, body: JSON.stringify({ username, password }) });
      setCsrf(session.csrfToken);
      setPassword(''); setAuthenticated(true);
    } catch (err) { setError(err instanceof Error ? err.message : 'Login failed.'); }
    finally { setLoginBusy(false); }
  };
  const logout = async () => {
    let nextCsrf = '';
    try {
      const session = await apiRequest<{ csrfToken: string }>('/auth/logout/', { method: 'POST', headers: { 'X-CSRFToken': csrf } });
      nextCsrf = session.csrfToken;
    } catch {
      // Refresh the anonymous token if the session expired before logout completed.
      try { nextCsrf = (await getCsrf()).csrfToken; } catch { /* Keep the login form available offline. */ }
    }
    setCsrf(nextCsrf);
    setAuthenticated(false); setDashboard(null); setEnquiries([]); setSelected(null); setToast('');
  };
  const saveSelected = async () => {
    if (!selected) return; setSaving(true); setError('');
    try { const updated = await apiRequest<Enquiry>(`/admin/enquiries/${selected.kind}/${selected.id}/`, { method: 'PATCH', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf }, body: JSON.stringify({ status: selected.status, internal_note: selected.internal_note }) }); setEnquiries(v => v.map(e => e.id === updated.id && e.kind === updated.kind ? { ...e, ...updated } : e)); setSelected(updated); setToast('Enquiry updated.'); await loadDashboard(); }
    catch (err) { setError(err instanceof Error ? err.message : 'Unable to update enquiry.'); }
    finally { setSaving(false); }
  };
  const localDateKey = (value: string) => { const date = new Date(value); return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`; };
  const filtered = enquiries.filter(e => {
    const key = localDateKey(e.created_at);
    const textMatches = `${e.name} ${e.company} ${e.email} ${e.requirement} ${e.kind}`.toLowerCase().includes(query.toLowerCase());
    const typeMatches = typeFilter === 'All' || (typeFilter === 'Quote Requests' ? e.kind === 'quote' : e.kind === 'contact');
    const statusMatches = statusFilter === 'All' || e.status === statusFilter;
    const fromMatches = !dateFrom || key >= dateFrom; const toMatches = !dateTo || key <= dateTo;
    return textMatches && typeMatches && statusMatches && fromMatches && toMatches;
  });
  const exportCsv = () => {
    const params = new URLSearchParams();
    if (typeFilter === 'Contact Enquiries') params.set('type', 'contact');
    else if (typeFilter === 'Quote Requests') params.set('type', 'quote');
    if (statusFilter !== 'All') params.set('status', statusFilter);
    if (dateFrom) params.set('from_date', dateFrom);
    if (dateTo) params.set('to_date', dateTo);
    if (query.trim()) params.set('q', query.trim());
    const queryString = params.toString();
    window.location.assign(`/api/admin/enquiries/export.csv${queryString ? `?${queryString}` : ''}`);
  };
  return <div className="admin-shell"><aside className="admin-sidebar"><div className="admin-mark"><span>NX</span><div><strong>NEXAGE</strong><small>ADMIN CONSOLE</small></div></div><div className="admin-side-active"><ClipboardList size={18} /> Enquiries</div><div className="admin-sidebar-meta"><ShieldCheck size={15} /><span>Authorized access only</span></div><a href="/" className="admin-back-link">← Return to website</a></aside><main className="admin-main">
    {!authenticated ? <div className="admin-login-wrap"><div className="admin-login-card"><span className="eyebrow"><span className="eyebrow-mark" />NEXAGE ADMINISTRATION</span><h1>Sign in to manage enquiries.</h1><p>This area is intended for authorized NexAge staff. Use your configured Django admin credentials.</p><form onSubmit={login} className="admin-login-form"><label>Username<input value={username} onChange={e => setUsername(e.target.value)} required autoComplete="username" /></label><label>Password<input value={password} onChange={e => setPassword(e.target.value)} required type="password" autoComplete="current-password" /></label><button className="button button--yellow" disabled={loginBusy}>{loginBusy ? 'Signing in…' : 'Sign in'} <ShieldCheck size={16} /></button>{error && <p className="admin-error" role="alert">{error}</p>}</form><p className="admin-note">Admin authentication is server-side. No password is stored in the website frontend.</p></div></div> : <>
      <div className="admin-topbar"><div><span className="eyebrow"><span className="eyebrow-mark" />MANAGEMENT CONSOLE</span><h1>Enquiry overview</h1><p>Review incoming website enquiries and track follow-up status.</p></div><div className="admin-top-actions"><button className="button button--outline-dark" onClick={() => void loadDashboard()} disabled={busy}><RefreshCw size={15} /> Refresh</button><button className="button button--outline-dark" onClick={exportCsv}><Download size={15} /> Export CSV</button><a className="button button--outline-dark" href="/backend-admin/">Content Admin ↗</a><button className="button button--black" onClick={() => void logout()}><LogOut size={15} /> Sign out</button></div></div>
      {error && <div className="admin-error-bar" role="alert">{error}</div>}{toast && <div className="admin-toast" role="status">{toast}<button onClick={() => setToast('')} aria-label="Dismiss notification">×</button></div>}
      <div className="admin-stat-grid">{[{ label: 'Total Enquiries', value: dashboard?.total_enquiries ?? '—', icon: ClipboardList }, { label: 'New Enquiries', value: dashboard?.new_enquiries ?? '—', icon: Activity }, { label: 'Quote Requests', value: dashboard?.quote_requests ?? '—', icon: FileText }, { label: 'Open Requests', value: dashboard?.open_requests ?? '—', icon: Users }, { label: 'Closed Requests', value: dashboard?.closed_requests ?? '—', icon: ShieldCheck }].map(s => { const Icon = s.icon; return <div className="admin-stat-card" key={s.label}><span className="admin-stat-icon"><Icon size={19} /></span><span>{s.label}</span><strong>{s.value}</strong></div>; })}</div>
      <div className="admin-content-grid"><section className="admin-list-panel"><div className="admin-list-heading"><div><h2>Incoming enquiries</h2><p>Search and select an enquiry to review its details.</p></div><span className="admin-count">{filtered.length} records</span></div><div className="admin-filters"><label><Search size={16} /><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search name, company, requirement…" /></label><select value={typeFilter} onChange={e => setTypeFilter(e.target.value)} aria-label="Filter by enquiry type"><option>All</option><option>Contact Enquiries</option><option>Quote Requests</option></select><select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} aria-label="Filter by status"><option>All</option>{statusOptions.map(s => <option key={s}>{s}</option>)}</select></div><div className="admin-date-filters"><label>From <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} aria-label="Filter from date" /></label><label>To <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} aria-label="Filter to date" /></label><button onClick={() => { setQuery(''); setStatusFilter('All'); setTypeFilter('All'); setDateFrom(''); setDateTo(''); }} disabled={!query && statusFilter === 'All' && typeFilter === 'All' && !dateFrom && !dateTo}>Clear filters</button></div><div className="admin-table-wrap"><table className="admin-table"><thead><tr><th>Enquiry</th><th>Type</th><th>Status</th><th>Date</th></tr></thead><tbody>{filtered.map(e => <tr key={`${e.kind}-${e.id}`} className={selected?.kind === e.kind && selected.id === e.id ? 'selected' : ''} onClick={() => { setSelected(e); setToast(''); }} tabIndex={0} onKeyDown={k => { if (k.key === 'Enter') setSelected(e); }}><td><strong>{e.name}</strong><small>{e.company || e.email}</small></td><td><span className={`kind-pill ${e.kind}`}>{e.kind === 'quote' ? 'Quote' : 'Contact'}</span></td><td><span className={`status-pill ${e.status.toLowerCase().replaceAll(' ', '-')}`}>{e.status}</span></td><td>{new Date(e.created_at).toLocaleDateString('en-IN')}</td></tr>)}</tbody></table>{!filtered.length && <div className="admin-no-results">No enquiries match the current filters.</div>}</div></section>
      <aside className="admin-detail-panel">{selected ? <><div className="admin-detail-head"><div><span className="eyebrow">{selected.kind === 'quote' ? 'QUOTE REQUEST' : 'CONTACT ENQUIRY'}</span><h2>{selected.name}</h2><p>{selected.company || 'Company not supplied'}</p></div><button className="detail-dismiss" onClick={() => setSelected(null)} aria-label="Close details">×</button></div><div className="admin-contact-details"><a href={`mailto:${selected.email}`}>{selected.email}</a>{selected.phone && <a href={`tel:${selected.phone}`}>{selected.phone}</a>}{selected.location && <span>{selected.location}</span>}</div><div className="admin-detail-block"><span>REQUIREMENT</span><p>{selected.requirement || 'Not supplied'}</p></div><div className="admin-detail-block"><span>MESSAGE / SCOPE</span><p className="admin-message">{selected.message || 'No additional message supplied.'}</p></div><label className="admin-control-label">Status<select value={selected.status} onChange={e => setSelected({ ...selected, status: e.target.value })}>{statusOptions.map(s => <option key={s}>{s}</option>)}</select></label><label className="admin-control-label">Internal note<textarea value={selected.internal_note || ''} onChange={e => setSelected({ ...selected, internal_note: e.target.value })} rows={4} placeholder="Add a private note for the NexAge team…" /></label><div className="admin-detail-foot">{selected.attachment_id ? <a className="download-link" href={`/api/admin/documents/${selected.attachment_id}/download/`}><ArrowDownToLine size={15} /> Download attachment</a> : <span className="admin-no-file">No attachment</span>}<button className="button button--yellow" onClick={() => void saveSelected()} disabled={saving}>{saving ? 'Saving…' : 'Save Changes'}</button></div></> : <div className="admin-empty-detail"><span><ClipboardList size={25} /></span><h3>Select an enquiry</h3><p>Customer contact details, requirement, attachments and internal notes will appear here.</p></div>}</aside></div>
      </>}
    </main></div>;
}
