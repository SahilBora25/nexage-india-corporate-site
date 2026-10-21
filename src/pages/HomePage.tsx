import { ArrowLeft, ArrowRight, ArrowUpRight, Check, Cpu, Layers3, Settings2, ShieldCheck, Workflow, Wrench } from 'lucide-react';
import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { partners, selectedClients, solutions } from '../data';
import { CTABand, ClientLogo, ImageBlock, PartnerLogo, ProductCard, ProjectCard, SectionTitle, SolutionCard } from '../components/Site';
import { useLiveAwards, useLiveIndustries, useLivePartners, useLiveProducts, useLiveProjects } from '../hooks/usePublicList';
import { LatestNewsSection } from './NewsUpdatesPage';

const capabilities = [
  { title: 'Industrial Automation', path: '/solutions/industrial-automation', icon: Workflow },
  { title: 'Conveyors & Material Handling', path: '/solutions/conveyor-material-handling', icon: Layers3 },
  { title: 'Smart Manufacturing', path: '/solutions/smart-manufacturing', icon: Cpu },
  { title: 'Industrial Tools', path: '/products/industrial-tools', icon: Wrench },
  { title: 'MRO & Services', path: '/services', icon: Settings2 },
];

const heroSlides = [
  { src: 'automation-line-ai.jpg', alt: 'Robotic automation line assembling a vehicle body', label: 'Industrial automation' },
  { src: 'tool-in-use-ai.jpg', alt: 'Technician using a torque tool at an assembly workstation', label: 'Precision assembly' },
  { src: 'hero-overhead-crane.webp', alt: 'Industrial crane hook and lifting equipment', label: 'Material handling' },
  { src: 'hero-maintenance-pump-ai.jpg', alt: 'Technician inspecting a centrifugal pump and motor', label: 'Industrial services' },
  { src: 'gantry-machine-ai.jpg', alt: 'Cartesian gantry handling a metal component in a guarded cell', label: 'Custom automation' },
  { src: 'pick-to-light-rack.jpg', alt: 'Operator collecting a component from a pick-to-light rack', label: 'Smart kitting' },
];

export default function HomePage() {
  const [slide, setSlide] = useState(0);
  const touchStart = useRef<number | null>(null);
  const liveProducts = useLiveProducts();
  const liveProjects = useLiveProjects();
  const livePartners = useLivePartners();
  const liveIndustries = useLiveIndustries();
  const liveAwards = useLiveAwards();

  // Prefer live CMS records but keep the profile-backed list available if the API is empty.
  const featuredPartners = livePartners.length ? livePartners : partners;

  return <>
    <section className="home-hero home-hero--slider" aria-label="NexAge industrial engineering" onKeyDown={event => { if (event.key === 'ArrowRight') setSlide(index => (index + 1) % heroSlides.length); if (event.key === 'ArrowLeft') setSlide(index => (index - 1 + heroSlides.length) % heroSlides.length); }} onTouchStart={event => { touchStart.current = event.touches[0]?.clientX ?? null; }} onTouchEnd={event => { const end = event.changedTouches[0]?.clientX; if (touchStart.current !== null && end !== undefined && Math.abs(end - touchStart.current) > 45) setSlide(index => (index + (end < touchStart.current! ? 1 : -1) + heroSlides.length) % heroSlides.length); touchStart.current = null; }}>
      <div className="hero-slider-image" role="img" aria-label={heroSlides[slide].alt} style={{ backgroundImage: `url('/images/${heroSlides[slide].src}')` }} key={heroSlides[slide].src} />
      <div className="hero-video-shade" aria-hidden="true" />
      <div className="wrap hero-inner">
        <div className="hero-copy">
          <span className="eyebrow"><span className="eyebrow-mark" />NEXAGE INDIA PVT. LTD.</span>
          <h1>Engineering Excellence.<br /><em>Safety First.</em></h1>
          <p className="hero-lead">Industrial automation, material handling and MRO for modern manufacturing.</p>
          <p className="hero-subcopy">From engineering and system integration to installation, commissioning and ongoing support.</p>
          <div className="hero-actions">
            <Link className="button button--yellow" to="/quote">Request a Quote <ArrowUpRight size={16} /></Link>
            <Link className="button button--outline-light" to="/solutions">Explore Solutions <ArrowRight size={16} /></Link>
          </div>
        </div>
      </div>
      <div className="hero-slider-controls" aria-label="Industrial photography slides">
        <button type="button" className="hero-slider-arrow" aria-label="Previous slide" onClick={() => setSlide(index => (index - 1 + heroSlides.length) % heroSlides.length)}><ArrowLeft size={18} /></button>
        <div className="hero-slider-dots">{heroSlides.map((item, index) => <button type="button" key={item.src} aria-label={`Show slide ${index + 1}: ${item.label}`} aria-pressed={slide === index} className={slide === index ? 'active' : ''} onClick={() => setSlide(index)} />)}</div>
        <span className="hero-slide-label" aria-live="polite">{heroSlides[slide].label}</span>
        <button type="button" className="hero-slider-arrow" aria-label="Next slide" onClick={() => setSlide(index => (index + 1) % heroSlides.length)}><ArrowRight size={18} /></button>
      </div>
    </section>

    <section className="home-capability-strip" aria-label="Core capabilities">
      <div className="wrap home-capability-strip-inner">
        {capabilities.map(({ title, path, icon: Icon }) => <Link to={path} key={title} className="home-capability-link"><Icon size={20} strokeWidth={1.7} /><span>{title}</span><ArrowUpRight size={14} className="capability-open" /></Link>)}
      </div>
    </section>

    <section id="home-solutions" className="section solutions-home home-solutions-section">
      <div className="wrap">
        <SectionTitle kicker="WHAT WE DO" title="Industrial solutions, made practical." text="Choose the capability that best matches your production or engineering requirement." action={{ label: 'View All Solutions', to: '/solutions' }} />
        <div className="solutions-grid home-solutions-grid">{solutions.slice(0, 4).map((item, i) => <SolutionCard key={item.slug} item={item} index={i} />)}</div>
      </div>
    </section>

    <section className="section about-home about-home--simple">
      <div className="wrap about-grid">
        <div className="about-photo-wrap">
          <ImageBlock src="engineering-team-ai.jpg" alt="Engineers reviewing a conveyor design at a factory workstation" className="about-photo" />
          <div className="photo-caption"><span className="caption-line" /><span>ENGINEERING WITH PURPOSE</span></div>
        </div>
        <div className="about-copy">
          <span className="eyebrow"><span className="eyebrow-mark" />ABOUT NEXAGE</span>
          <h2>One engineering partner, from concept to commissioning.</h2>
          <p>NexAge India supports manufacturing environments with industrial automation, conveyor systems, custom machines, process integration, fabrication and industrial services.</p>
          <div className="about-checklist about-checklist--simple">
            <div><Check size={16} />Application-led engineering</div>
            <div><Check size={16} />Integrated equipment and systems</div>
            <div><Check size={16} />Installation and ongoing MRO support</div>
          </div>
          <Link className="button button--black" to="/about">About NexAge <ArrowRight size={16} /></Link>
        </div>
      </div>
    </section>

    <section className="smart-banner smart-banner--simple">
      <div className="smart-image" style={{ backgroundImage: "url('/images/industrial-dashboard-ai.jpg')" }} aria-hidden="true" />
      <div className="wrap smart-content">
        <span className="eyebrow"><span className="eyebrow-mark" />SMART MANUFACTURING</span>
        <h2>Clearer processes.<br />Better visibility.</h2>
        <p>Explore guided picking, Jidoka / Poka-Yoke, condition monitoring and Industrial IoT concepts for real production environments.</p>
        <Link className="button button--yellow" to="/solutions/smart-manufacturing">Explore Smart Manufacturing <ArrowRight size={16} /></Link>
      </div>
    </section>

    <section className="section featured-products home-products-section">
      <div className="wrap">
        <SectionTitle kicker="PRODUCTS & SYSTEMS" title="Equipment and systems for the job." text="Browse NexAge-developed solutions alongside clearly identified partner products and integrated systems." action={{ label: 'View Product Catalogue', to: '/products' }} />
        <div className="products-grid">{liveProducts.slice(0, 3).map(item => <ProductCard key={item.slug} item={item} />)}</div>
        <div className="partner-note"><ShieldCheck size={18} /><span>Partner product ownership and relationships are identified clearly.</span><Link to="/partners">View Partners <ArrowRight size={15} /></Link></div>
      </div>
    </section>

    <section className="section home-industries-section">
      <div className="wrap">
        <SectionTitle kicker="INDUSTRIES WE SERVE" title="Built around real production environments." text="Explore representative industries connected to NexAge’s engineering, automation and material-handling capabilities." action={{ label: 'View Industries', to: '/industries' }} />
        <div className="industry-page-grid home-industry-grid">{liveIndustries.slice(0, 3).map((item, index) => <article className="industry-page-card" key={item.slug}><ImageBlock src={item.image} alt={`${item.title} industrial environment`} /><div className="industry-page-copy"><span>0{index + 1} / INDUSTRY</span><h3>{item.title}</h3><p>{item.description}</p><Link className="text-link" to="/industries">Explore industry <ArrowRight size={15} /></Link></div></article>)}</div>
      </div>
    </section>

    <section className="section projects-home home-projects-section">
      <div className="wrap">
        <SectionTitle kicker="SELECTED APPLICATIONS" title="Engineering applied on the factory floor." text="Explore project categories drawn from NexAge’s company profile; customer-specific results are shown only when verified." action={{ label: 'Explore Projects', to: '/projects' }} />
        <div className="projects-grid">{liveProjects.slice(0, 3).map((item, i) => <ProjectCard key={item.slug} item={item} index={i} />)}</div>
      </div>
    </section>

    <section className="section home-recognition-section">
      <div className="wrap home-recognition-wrap">
        <div><span className="eyebrow"><span className="eyebrow-mark" />PROFILE-RECORDED RECOGNITION</span><h2>Recognition from industry partners.</h2><p>These award references are reproduced from the NexAge company profile; see the recognition page for context.</p></div>
        <div className="home-recognition-list">{liveAwards.slice(0, 3).map(item => <div key={`${item.title}-${item.period}`}><span>{item.period}</span><strong>{item.title}</strong></div>)}<Link className="text-link" to="/awards">Awards & recognition <ArrowRight size={15} /></Link></div>
      </div>
    </section>

    <section className="partners-band partners-band--simple">
      <div className="wrap">
        <div className="partners-band-heading">
          <div><span className="eyebrow"><span className="eyebrow-mark" />DOCUMENTED PARTNERSHIPS</span><h2>Trusted brands. <em>Integrated by NexAge.</em></h2><p>Partner relationships are presented according to the NexAge company profile.</p></div>
          <Link className="text-link" to="/partners">Meet Our Partners <ArrowRight size={16} /></Link>
        </div>
        <div className="partner-logo-row">{featuredPartners.slice(0, 5).map((partner) => <Link className="partner-logo-tile" to="/partners" key={partner.name} aria-label={`View ${partner.name} partner relationship`}><PartnerLogo name={partner.name} /></Link>)}</div>
      </div>
    </section>

    <section className="home-clients-band">
      <div className="wrap home-clients-inner">
        <div className="home-clients-copy"><span className="eyebrow"><span className="eyebrow-mark" />CLIENTS & LOCATIONS</span><h2>Industrial relationships across India.</h2><p>See the client names and locations listed in the NexAge company profile.</p><Link className="text-link" to="/clients">Explore Clients <ArrowRight size={16} /></Link></div>
        <div className="partner-logo-row home-client-logo-grid" role="list" aria-label="Selected client logos">{selectedClients.map(name => <div className="partner-logo-tile" role="listitem" key={name}><ClientLogo name={name} /></div>)}</div>
      </div>
    </section>

    <LatestNewsSection />
    <CTABand />
  </>;
}
