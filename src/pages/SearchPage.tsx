import { FormEvent, useEffect, useMemo, useState } from 'react';
import { ArrowRight, ArrowUpRight, Search as SearchIcon } from 'lucide-react';
import { Link, useSearchParams } from 'react-router-dom';
import { solutions } from '../data';
import { AssetImage, PageIntro } from '../components/Site';
import { useLiveIndustries, useLivePartners, useLiveProducts, useLiveProjects, useLiveServices } from '../hooks/usePublicList';

type Result = { title: string; path: string; type: string; description: string; image?: string };
export default function SearchPage() {
  const [params, setParams] = useSearchParams(); const initial = params.get('q') || ''; const [value, setValue] = useState(initial);
  useEffect(() => setValue(initial), [initial]);
  const liveProducts = useLiveProducts(); const liveProjects = useLiveProjects(); const liveIndustries = useLiveIndustries(); const liveServices = useLiveServices(); const livePartners = useLivePartners();
  const results = useMemo<Result[]>(() => {
    const q = initial.trim().toLowerCase(); if (!q) return [];
    const all: Result[] = [
      ...solutions.map(i => ({ title: i.title, path: i.path, type: 'Solution', description: i.description, image: i.image })),
      ...liveProducts.map(i => ({ title: i.title, path: i.path, type: 'Product', description: i.description, image: i.image })),
      ...liveProjects.map(i => ({ title: i.title, path: i.path, type: 'Application', description: i.description, image: i.image })),
      ...liveIndustries.map(i => ({ title: i.title, path: i.path, type: 'Industry', description: i.description, image: i.image })),
      ...liveServices.map(i => ({ title: i.title, path: '/services', type: 'Service', description: i.text, image: i.image })),
      ...livePartners.map(i => ({ title: i.name, path: '/partners', type: 'Partner', description: `${i.relationship}. ${i.text}` })),
      { title: 'Awards & Recognition', path: '/awards', type: 'Company', description: 'Documented awards and customer appreciation references.' },
    ];
    return all.filter(i => `${i.title} ${i.type} ${i.description}`.toLowerCase().includes(q)).slice(0, 40);
  }, [initial, liveProducts, liveProjects, liveIndustries, liveServices, livePartners]);
  const submit = (e: FormEvent) => { e.preventDefault(); setParams(value.trim() ? { q: value.trim() } : {}); };
  return <><PageIntro eyebrow="SEARCH NEXAGE" crumb="Search" title="Find the right capability." text="Search solutions, products, projects, services and industries." /><section className="section search-results-section"><div className="wrap"><form className="search-page-form" onSubmit={submit}><SearchIcon size={21} /><input value={value} onChange={e => setValue(e.target.value)} placeholder="Search NexAge" aria-label="Search NexAge" /><button className="button button--yellow">Search <ArrowRight size={16} /></button></form>{!initial.trim() ? <div className="search-empty"><h2>What can we help you find?</h2><p>Try terms like automation, conveyor, Jidoka, wireless, tools or MRO.</p></div> : <div className="search-result-wrap"><div className="search-result-heading"><div><span className="eyebrow"><span className="eyebrow-mark" />SEARCH RESULTS</span><h2>Results for “{initial}”</h2></div><span>{results.length} {results.length === 1 ? 'result' : 'results'}</span></div>{results.length ? <div className="search-result-grid">{results.map((r, i) => <Link className="search-result" to={r.path} key={`${r.title}-${r.type}-${i}`}>{r.image && <AssetImage src={r.image} alt="" loading="lazy" />}<div><span>{r.type}</span><h3>{r.title}</h3><p>{r.description}</p><strong>View details <ArrowUpRight size={15} /></strong></div></Link>)}</div> : <div className="search-empty"><h2>No matching results found.</h2><p>Try a broader phrase, or browse all <Link to="/solutions">solutions</Link> and <Link to="/products">products</Link>.</p></div>}</div>}</div></section></>;
}
