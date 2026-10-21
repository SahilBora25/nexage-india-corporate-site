import { FormEvent, useEffect, useMemo, useState } from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { ArrowDownRight, ArrowRight, ArrowUpRight, CheckCircle2, ChevronDown, Factory, Menu, Search, ShieldCheck, X } from 'lucide-react';
import { awards, industries, pageMeta, partners, products, projects, services, solutions } from '../data';

export function imageUrl(src: string) {
  const value = String(src || '').trim();
  if (!value) return '';
  if (/^(https?:|data:|blob:)/i.test(value)) return value;
  // Normalise image paths that may come from the CMS, static data, or a public/ prefixed value.
  const clean = value.replace(/^\.\//, '').replace(/^public\//i, '').replace(/^\/+/, '');
  if (clean.startsWith('images/') || clean.startsWith('videos/')) return `/${clean}`;
  if (clean.startsWith('media/') || clean.startsWith('api/')) return `/${clean}`;
  return `/images/${clean}`;
}

const imageDescriptions: Record<string, string> = {
  'pick-to-light-rack.jpg': 'Operator selecting a component from illuminated pick-to-light bins',
  'pick-to-light-detail.jpg': 'Close view of illuminated bin indicators on a smart-kitting rack',
  'jidoka-poka-yoke-ai.jpg': 'Error-proofing assembly fixture with part sensors and status lights',
  'plc-monitoring-ai.jpg': 'Open control cabinet with PLC modules, organized wiring and an HMI',
  'industrial-dashboard-ai.jpg': 'Factory production-monitoring screens beside an automated line',
  'electronics-testing-ai.jpg': 'Technician testing a control board with probes and measurement instruments',
  'machine-relocation-ai.jpg': 'Rigging crew moving a large machine on heavy-duty machinery skates',
  'engineering-team-ai.jpg': 'Engineers reviewing a conveyor CAD model together',
  'engineering-design-ai.jpg': 'Engineer working on a CAD layout for industrial equipment',
  'maintenance-technician-ai.jpg': 'Technician inspecting an industrial motor and pump coupling',
  'condition-monitoring-ai.jpg': 'Technician measuring vibration on a motor bearing housing',
  'torque-tool-range-ai.jpg': 'Range of electric industrial tightening and torque tools',
  'tool-in-use-ai.jpg': 'Technician fastening a gearbox component with an electric torque tool',
  'lift-table-ai.jpg': 'Hydraulic scissor lift table supporting a secured industrial component',
  'gantry-machine-ai.jpg': 'Cartesian gantry machine transferring a component within safety guarding',
  'automation-line-ai.jpg': 'Robotic arms welding a vehicle body on an automated assembly line',
  'robotic-inspection-ai.jpg': 'Machine-vision camera inspecting a metal part in a guarded robot cell',
  'commissioning-team-ai.jpg': 'Commissioning technicians checking a conveyor HMI and sensor connection',
  'food-beverage-ai.jpg': 'Stainless bottling and filling equipment on a food-production conveyor',
  'jig-fixture-ai.jpg': 'Machined assembly fixture with locators, clamps and a positioned component',
  'precision-inspection-ai.jpg': 'Coordinate measuring probe inspecting a machined metal component',
  'hero-maintenance-pump-ai.jpg': 'Technician inspecting an industrial centrifugal pump and motor',
  'manipulator-ai.jpg': 'Overhead pneumatic manipulator lifting a component with a balanced arm',
  'industrial-integration-ai.jpg': 'Guarded robot transferring machined parts between a machine and conveyor',
};

function describeImage(src: string, fallback: string) {
  const filename = src.split(/[\\/]/).pop() || '';
  return imageDescriptions[filename] || fallback;
}

/** Image renderer with sensible local fallbacks so missing assets never show broken-image icons. */
export function AssetImage({ src, alt, className = '', loading = 'lazy' }: { src: string; alt: string; className?: string; loading?: 'lazy' | 'eager' }) {
  // Avoid a shared factory-photo fallback, which silently repeats unrelated imagery across cards.
  // A missing or broken asset uses the labelled placeholder below instead.
  const candidates = useMemo(() => { const resolved = imageUrl(src); return resolved ? [resolved] : []; }, [src]);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => { setAttempt(0); }, [src]);
  if (attempt >= candidates.length) {
    return <span className={`asset-image-fallback ${className}`} role="img" aria-label={alt || 'Industrial image'}><Factory size={28} aria-hidden="true" /><span>{alt || 'Industrial image'}</span></span>;
  }
  return <img className={className} src={candidates[attempt]} alt={describeImage(src, alt)} loading={loading} decoding="async" onError={() => setAttempt(current => Math.min(current + 1, candidates.length))} />;
}

const navItems = [
  { label: 'Home', to: '/' },
  { label: 'About Us', to: '/about' },
  { label: 'Solutions', to: '/solutions', menu: solutions.slice(0, 6) },
  { label: 'Products', to: '/products', menu: products.slice(0, 4) },
  { label: 'Industries', to: '/industries' },
  { label: 'Projects', to: '/projects' },
  { label: 'Partners', to: '/partners' },
  { label: 'Clients', to: '/clients' },
  { label: 'Services', to: '/services' },
  { label: 'Contact', to: '/contact' },
];

const partnerLogoConfig = (name: string): { src: string; theme: string } => {
  const normalized = name.toLowerCase();
  if (normalized.includes('kito') || normalized.includes('crosby')) return { src: '/images/partners/kito-crosby.png', theme: 'kito' };
  if (normalized.includes('desoutter')) return { src: '/images/partners/desoutter.png', theme: 'desoutter' };
  if (normalized.includes('tohnichi')) return { src: '/images/partners/tohnichi.png', theme: 'tohnichi' };
  if (normalized.includes('tone')) return { src: 'https://www.tonetool.co.jp/assets/img/common/logo_white.svg', theme: 'tone' };
  if (normalized.includes('durofix')) return { src: '/images/partners/durofix.jpg', theme: 'durofix' };
  return { src: '', theme: 'text' };
};

export function PartnerLogo({ name }: { name: string }) {
  const logo = partnerLogoConfig(name);
  const [failed, setFailed] = useState(false);
  useEffect(() => { setFailed(false); }, [logo.src]);
  const showAsset = Boolean(logo.src) && !failed;
  return <div className={`partner-logo-art partner-logo-art--${showAsset ? logo.theme : 'text'}`}>
    {showAsset ? <img src={logo.src} alt={`${name} logo`} loading="lazy" decoding="async" onError={() => setFailed(true)} /> : <strong>{name}</strong>}
  </div>;
}

const clientLogoConfig = (name: string): { src: string; theme: string } => {
  const normalized = name.toLowerCase();
  if (normalized.includes('tata motors')) return { src: 'https://commons.wikimedia.org/wiki/Special:FilePath/Tata_Motors_Logo.svg', theme: 'tata' };
  if (normalized.includes('ashok leyland')) return { src: 'https://commons.wikimedia.org/wiki/Special:FilePath/Ashok_Leyland_Logo.JPG?width=280', theme: 'ashok-leyland' };
  if (normalized.includes('titan')) return { src: 'https://commons.wikimedia.org/wiki/Special:FilePath/Titan_Company_Logo.png?width=180', theme: 'titan' };
  if (normalized.includes('henkel')) return { src: 'https://commons.wikimedia.org/wiki/Special:FilePath/Henkel-Logo.svg', theme: 'henkel' };
  if (normalized.includes('nestl')) return { src: 'https://commons.wikimedia.org/wiki/Special:FilePath/Nestle_textlogo_blue.svg', theme: 'nestle' };
  if (normalized.includes('denso')) return { src: 'https://commons.wikimedia.org/wiki/Special:FilePath/Denso.svg', theme: 'denso' };
  if (normalized.includes('honda')) return { src: 'https://commons.wikimedia.org/wiki/Special:FilePath/Honda_logo.svg', theme: 'honda' };
  if (normalized.includes('kubota')) return { src: 'https://commons.wikimedia.org/wiki/Special:FilePath/Kubota_Logo.svg', theme: 'kubota' };
  if (normalized.includes('mahindra')) return { src: 'https://commons.wikimedia.org/wiki/Special:FilePath/Mahindra_Rise_New_Logo.svg', theme: 'mahindra' };
  return { src: '', theme: 'text' };
};

export function ClientLogo({ name }: { name: string }) {
  const logo = clientLogoConfig(name);
  const [failed, setFailed] = useState(false);
  useEffect(() => { setFailed(false); }, [logo.src]);
  const showAsset = Boolean(logo.src) && !failed;
  return <div className={`partner-logo-art partner-logo-art--client partner-logo-art--client-${logo.theme}`} role="img" aria-label={`${name} client logo`}>
    {showAsset ? <img src={logo.src} alt={`${name} logo`} loading="lazy" decoding="async" onError={() => setFailed(true)} /> : <strong>{name}</strong>}
  </div>;
}

export function Brand({ dark = false }: { dark?: boolean }) {
  const [logoStage, setLogoStage] = useState(0);
  const logoPath = logoStage === 0 ? '/images/nexage-logo.jpg' : '/images/nexage-mark.webp';
  return <Link to="/" className={`brand ${dark ? 'brand--dark' : ''}`} aria-label="NexAge India homepage">
    {logoStage < 2 ? <img className={logoStage === 1 ? 'brand-mark-fallback' : ''} src={logoPath} alt="NexAge — Work for Satisfaction" onError={() => setLogoStage(stage => Math.min(stage + 1, 2))} /> : <span className="brand-text-fallback"><strong>NEXAGE</strong><small>Work for Satisfaction</small></span>}
  </Link>;
}

export function SiteHeader() {
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [query, setQuery] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  useEffect(() => { setMobileOpen(false); setOpenMenu(null); setSearchOpen(false); }, [location.pathname]);
  const submitSearch = (e: FormEvent) => { e.preventDefault(); const q = query.trim(); if (q) navigate(`/search?q=${encodeURIComponent(q)}`); setSearchOpen(false); };
  return <>
    <a className="skip-link" href="#main-content">Skip to content</a>
    <header className="site-header">
      <div className="header-inner wrap">
        <Brand />
        <nav className="desktop-nav" aria-label="Main navigation">
          {navItems.map(item => item.menu ? <div key={item.label} className="nav-menu-wrap" onMouseEnter={() => setOpenMenu(item.label)} onMouseLeave={() => setOpenMenu(null)}>
            <NavLink to={item.to} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} onClick={() => setOpenMenu(null)}>{item.label}<ChevronDown size={14} strokeWidth={1.8} /></NavLink>
            {item.label === 'Solutions' && openMenu === 'Solutions' && <div className="mega-menu">
              <div className="mega-intro"><span className="eyebrow">ENGINEERING CAPABILITIES</span><h3>Solutions built around your process.</h3><Link to="/solutions" className="text-link">Explore all solutions <ArrowRight size={15} /></Link></div>
              <div className="mega-links">{item.menu.map(m => <Link key={m.path} to={m.path}><span>{m.title}</span><ArrowUpRight size={15} /></Link>)}</div>
            </div>}
            {item.label === 'Products' && openMenu === 'Products' && <div className="mega-menu mega-menu--products">
              <div className="mega-intro"><span className="eyebrow">PRODUCTS & SYSTEMS</span><h3>Designed, integrated and sourced with care.</h3><Link to="/products" className="text-link">Browse products <ArrowRight size={15} /></Link></div>
              <div className="mega-links">{item.menu.map(m => <Link key={m.path} to={m.path}><span>{m.title}</span><ArrowUpRight size={15} /></Link>)}</div>
            </div>}
          </div> : <NavLink key={item.label} to={item.to} end={item.to === '/'} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>{item.label}</NavLink>)}
        </nav>
        <div className="header-actions"><button className="icon-button" aria-label="Search website" onClick={() => setSearchOpen(true)}><Search size={19} /></button><Link className="button button--yellow button--small quote-top" to="/quote">Request a Quote <ArrowUpRight size={15} /></Link><button className="icon-button mobile-trigger" aria-label={mobileOpen ? 'Close navigation' : 'Open navigation'} onClick={() => setMobileOpen(v => !v)}>{mobileOpen ? <X size={22} /> : <Menu size={22} />}</button></div>
      </div>
      {mobileOpen && <div className="mobile-nav"><div className="mobile-nav-inner">{navItems.map(item => <Link key={item.label} to={item.to} onClick={() => setMobileOpen(false)}>{item.label}<ArrowUpRight size={16} /></Link>)}<Link className="button button--yellow" to="/quote" onClick={() => setMobileOpen(false)}>Request a Quote <ArrowUpRight size={16} /></Link><a href="tel:+919219586605" className="mobile-phone">+91 92195 86605</a></div></div>}
    </header>
    {searchOpen && <div className="search-overlay" role="dialog" aria-modal="true" aria-label="Search NexAge website"><button className="icon-button search-close" onClick={() => setSearchOpen(false)} aria-label="Close search"><X /></button><div className="search-modal wrap"><span className="eyebrow">SEARCH NEXAGE</span><h2>What are you looking for?</h2><form onSubmit={submitSearch} className="search-form"><Search size={21} /><input autoFocus value={query} onChange={e => setQuery(e.target.value)} placeholder="Try “Jidoka”, “conveyor” or “MRO”" aria-label="Search products, solutions and projects" /><button type="submit" className="button button--yellow">Search <ArrowRight size={17} /></button></form><p>Search solutions, products, applications, services and industries.</p></div></div>}
  </>;
}

export function SiteFooter() {
  return <footer className="site-footer"><div className="wrap footer-main">
    <div className="footer-brand-col"><Brand dark /><p>Engineering solutions for modern manufacturing — from automation and material handling to MRO support.</p><div className="footer-tag"><ShieldCheck size={16} /> Engineering Excellence. Safety First.</div></div>
    <div className="footer-col"><h3>Explore</h3><Link to="/about">About NexAge</Link><Link to="/solutions">Solutions</Link><Link to="/products">Products</Link><Link to="/industries">Industries</Link><Link to="/projects">Projects</Link></div>
    <div className="footer-col"><h3>Company</h3><Link to="/partners">Partners</Link><Link to="/clients">Clients</Link><Link to="/services">Services</Link><Link to="/awards">Awards & Recognition</Link><Link to="/news">News & Updates</Link><Link to="/contact">Contact</Link><Link to="/quote">Request a Quote</Link><Link to="/privacy">Privacy Notice</Link><Link to="/terms">Terms of Use</Link></div>
    <div className="footer-col footer-contact"><h3>Get in touch</h3><strong>Office</strong><p>B1/14–21, Metropolis City,<br />Near Radisson Hotel, Rudrapur,<br />Udham Singh Nagar, Uttarakhand 263153</p><strong>Works</strong><p>Plot No. 62 D, Sector-4,<br />IIE-SIDCUL, Pantnagar,<br />Uttarakhand 263153</p><a href="tel:+919219586605">+91 92195 86605</a><a href="tel:+919258020512">+91 92580 20512</a><a href="mailto:sales@nexageindia.com">sales@nexageindia.com</a></div>
  </div><div className="footer-bottom"><div className="wrap footer-bottom-inner"><span>© {new Date().getFullYear()} NexAge India Pvt. Ltd. All rights reserved.</span><span>Built around engineering. Grounded in safety.</span></div></div></footer>;
}

export function SectionTitle({ kicker, title, text, light = false, action }: { kicker: string; title: string; text?: string; light?: boolean; action?: { label: string; to: string } }) {
  return <div className={`section-title ${light ? 'section-title--light' : ''}`}><div><span className="eyebrow"><span className="eyebrow-mark" />{kicker}</span><h2>{title}</h2>{text && <p>{text}</p>}</div>{action && <Link className="text-link" to={action.to}>{action.label}<ArrowRight size={16} /></Link>}</div>;
}

export function PageIntro({ eyebrow, title, text, image, dark = false, crumb }: { eyebrow: string; title: string; text: string; image?: string; dark?: boolean; crumb?: string }) {
  return <section className={`page-intro ${dark ? 'page-intro--dark' : ''} ${image ? 'page-intro--image' : ''}`} style={image ? { backgroundImage: `linear-gradient(90deg, rgba(13,14,15,.92) 0%, rgba(13,14,15,.76) 44%, rgba(13,14,15,.22) 100%), url('${imageUrl(image)}')` } : undefined}>
    <div className="wrap page-intro-content">{crumb && <div className="breadcrumbs"><Link to="/">Home</Link><span>/</span><span>{crumb}</span></div>}<span className="eyebrow"><span className="eyebrow-mark" />{eyebrow}</span><h1>{title}</h1><p>{text}</p></div>
    <div className="intro-index">NEXAGE <span>///</span> ENGINEERING</div>
  </section>;
}

export function ImageBlock({ src, alt, className = '', loading = 'lazy' }: { src: string; alt: string; className?: string; loading?: 'lazy' | 'eager' }) {
  return <div className={`image-block ${className}`}><AssetImage src={src} alt={alt} loading={loading} /><span className="image-corner" aria-hidden="true" /></div>;
}

export function SolutionCard({ item, index = 0 }: { item: typeof solutions[number]; index?: number }) {
  return <Link to={item.path} className={`solution-card ${index % 3 === 1 ? 'solution-card--tall' : ''}`}><ImageBlock src={item.image} alt={`${item.title} industrial application`} /><div className="solution-card-copy"><span className="card-index">0{index + 1} / CAPABILITY</span><h3>{item.title}</h3><p>{item.description}</p><span className="card-arrow"><ArrowUpRight size={19} /></span></div></Link>;
}

export function ProductCard({ item }: { item: typeof products[number] }) {
  return <article className="product-card"><Link to={item.path} className="product-image"><AssetImage src={item.image} alt={item.title} loading="lazy" /><span className="product-type">{item.type}</span><span className="product-card-arrow"><ArrowUpRight size={17} /></span></Link><div className="product-card-copy"><span className="eyebrow">{item.category}</span><h3><Link to={item.path}>{item.title}</Link></h3><p>{item.description}</p><Link className="text-link" to={item.path}>View details <ArrowRight size={15} /></Link></div></article>;
}

export function ProjectCard({ item, index = 0 }: { item: typeof projects[number]; index?: number }) {
  return <article className="project-card"><Link to={item.path} className="project-image"><AssetImage src={item.image} alt={item.title} loading="lazy" /><span className="project-index">0{index + 1}</span><span className="project-open"><ArrowUpRight size={18} /></span></Link><div className="project-copy"><span className="eyebrow">{item.category}</span><h3>{item.title}</h3><p>{item.description}</p></div></article>;
}

export function TrustStrip() {
  return <div className="trust-strip"><div className="wrap trust-strip-inner"><div><ShieldCheck size={20} /><span><strong>Safety-first mindset</strong><small>Built into the way we work</small></span></div><div><Factory size={20} /><span><strong>Engineering-led delivery</strong><small>From concept to commissioning</small></span></div><div><CheckCircle2 size={20} /><span><strong>Integrated capabilities</strong><small>Systems, tools and services</small></span></div><div><ArrowDownRight size={20} /><span><strong>Customer collaboration</strong><small>Clear scope, practical solutions</small></span></div></div></div>;
}

export function CTABand() {
  return <section className="cta-band"><div className="cta-image" style={{ backgroundImage: "linear-gradient(90deg, rgba(9,10,10,.95), rgba(9,10,10,.8) 54%, rgba(9,10,10,.34)), url('/images/cta-background.webp')" }} /><div className="wrap cta-content"><span className="eyebrow"><span className="eyebrow-mark" />LET’S SOLVE THE RIGHT PROBLEM</span><h2>Have an automation or engineering challenge?</h2><p>Let’s discuss the right solution for your application.</p><div className="cta-actions"><Link className="button button--yellow" to="/quote">Request a Quote <ArrowUpRight size={16} /></Link><Link className="button button--outline-light" to="/contact">Contact NexAge <ArrowRight size={16} /></Link></div></div></section>;
}

export function SEO() {
  const location = useLocation();
  const routeItem = useMemo(() => [...solutions, ...products, ...projects].find(item => item.path === location.pathname), [location.pathname]);
  const page = useMemo(() => {
    if (pageMeta[location.pathname]) return pageMeta[location.pathname];
    const slug = location.pathname.split('/').filter(Boolean).pop() || 'Industrial Engineering';
    const label = slug.split('-').map(word => word ? word[0].toUpperCase() + word.slice(1) : '').join(' ');
    return { title: `${label} | NexAge India`, description: `Explore ${label.toLowerCase()} applications, engineering capabilities and integrated industrial solutions from NexAge India Pvt. Ltd.` };
  }, [location.pathname]);
  const previewImage = routeItem?.introImage || routeItem?.detailImage || routeItem?.image || ({
    '/': 'hero-automation-line.webp',
    '/about': 'engineering-team-ai.jpg',
    '/solutions': 'industrial-dashboard-ai.jpg',
    '/products': 'torque-tool-range-ai.jpg',
    '/industries': 'food-beverage-ai.jpg',
    '/projects': 'pick-to-light-rack.jpg',
    '/partners': 'partners/kito-crosby.png',
    '/clients': 'clients/india-client-map.jpg',
    '/services': 'maintenance-technician-ai.jpg',
    '/awards': 'warehouse-logistics.webp',
    '/contact': 'engineering-team-ai.jpg',
    '/quote': 'engineering-team-ai.jpg',
  } as Record<string, string>)[location.pathname] || 'hero-automation-line.webp';
  const absolutePreviewImage = `https://www.nexageindia.com${imageUrl(previewImage)}`;
  useEffect(() => {
    document.title = page.title;
    const setMeta = (kind: 'name' | 'property', key: string, content: string) => {
      let meta = document.querySelector<HTMLMetaElement>(`meta[${kind}="${key}"]`);
      if (!meta) { meta = document.createElement('meta'); meta.setAttribute(kind, key); document.head.appendChild(meta); }
      meta.setAttribute('content', content);
    };
    setMeta('name', 'description', page.description);
    const canonical = document.querySelector('link[rel="canonical"]');
    if (canonical) canonical.setAttribute('href', `https://www.nexageindia.com${location.pathname}`);
    setMeta('property', 'og:title', page.title);
    setMeta('property', 'og:description', page.description);
    setMeta('property', 'og:url', `https://www.nexageindia.com${location.pathname}`);
    setMeta('property', 'og:image', absolutePreviewImage);
    setMeta('property', 'og:image:alt', page.title);
    setMeta('name', 'twitter:title', page.title);
    setMeta('name', 'twitter:description', page.description);
    setMeta('name', 'twitter:image', absolutePreviewImage);
    setMeta('name', 'twitter:card', 'summary_large_image');
    setMeta('name', 'robots', location.pathname === '/admin' ? 'noindex,nofollow' : 'index,follow,max-image-preview:large');
    window.scrollTo(0, 0);
  }, [location.pathname, page, absolutePreviewImage]);
  return null;
}
