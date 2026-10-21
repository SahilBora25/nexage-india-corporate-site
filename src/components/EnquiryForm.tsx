import { FormEvent, useState } from 'react';
import { ArrowUpRight, Check } from 'lucide-react';
import { Link } from 'react-router-dom';
import { submitEnquiry } from '../api';

const interests = ['Industrial Automation', 'Conveyor / Material Handling', 'Pick-to-Light', 'Jidoka / Poka-Yoke', 'Special Purpose Machine', 'Industrial Tools', 'Cranes / Hoists', 'MRO / AMC', 'IoT / Industry 4.0', 'Wireless TX/RX', 'Other'];

/** Single enquiry form for the home page; submits to the quote endpoint so the admin panel keeps its existing flow. */
export default function EnquiryForm() {
  const [state, setState] = useState<'idle' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const submit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault(); setBusy(true); setState('idle'); setMessage('');
    const form = e.currentTarget;
    const file = (form.elements.namedItem('attachment') as HTMLInputElement | null)?.files?.[0];
    if (file && file.size > 10 * 1024 * 1024) { setBusy(false); setState('error'); setMessage('The selected file is larger than 10 MB. Please choose a smaller file.'); return; }
    try { await submitEnquiry('quote', new FormData(form)); setState('success'); setMessage('Thank you. Your enquiry has been received. Our team will contact you shortly.'); form.reset(); }
    catch (err) { setState('error'); setMessage(err instanceof Error ? err.message : 'Unable to submit your enquiry. Please try again.'); }
    finally { setBusy(false); }
  };
  return <form className="enquiry-form quote-form" onSubmit={submit}>
    <div className="form-card-heading"><span className="eyebrow"><span className="eyebrow-mark" />SEND AN ENQUIRY</span><h2>How can we help?</h2><p>Fields marked with * are required.</p></div>
    <div className="form-grid">
      <label>Full Name *<input name="name" required autoComplete="name" maxLength={120} /></label>
      <label>Company *<input name="company" required autoComplete="organization" maxLength={160} /></label>
      <label>Email *<input name="email" type="email" required autoComplete="email" maxLength={254} /></label>
      <label>Phone *<input name="phone" required autoComplete="tel" maxLength={32} /></label>
      <label className="field-full">Interested In *<select name="requirement" required defaultValue=""><option value="" disabled>Select a solution or service</option>{interests.map(v => <option key={v}>{v}</option>)}</select></label>
      <label className="field-full">Project Requirement *<textarea name="project_requirement" required rows={4} maxLength={6000} placeholder="Describe the process, equipment, challenge or desired scope..." /></label>
      <label className="field-full upload-field">Upload Drawing / Document<input name="attachment" type="file" accept=".pdf,.jpg,.jpeg,.png,.docx,.xlsx" /><small>Optional. PDF, JPG, PNG, DOCX or XLSX · Maximum 10 MB.</small></label>
      <label className="honeypot" aria-hidden="true">Website<input tabIndex={-1} autoComplete="off" name="website" /></label>
    </div>
    <button className="button button--yellow form-submit" type="submit" disabled={busy}>{busy ? 'Submitting…' : 'Send Enquiry'} <ArrowUpRight size={16} /></button>
    {state !== 'idle' && <div className={`form-feedback ${state}`} role="status">{state === 'success' && <Check size={17} />}{message}</div>}
    <p className="form-privacy">Please avoid including passwords or other confidential credentials. <Link to="/privacy">Read our privacy notice.</Link></p>
  </form>;
}
