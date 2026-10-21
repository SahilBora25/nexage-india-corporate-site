import { ArrowLeft, ArrowRight, ArrowUpRight, Check, Cpu, Layers3, Mail, MapPin, Phone, Settings2, ShieldCheck, Workflow, Wrench } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { leadership, partners, selectedClients, solutions } from '../data';
import { ClientLogo, ImageBlock, PartnerLogo, ProductCard, SectionTitle, SolutionCard } from '../components/Site';
import EnquiryForm from '../components/EnquiryForm';
import { useLivePartners, useLiveProducts } from '../hooks/usePublicList';

const capabilities = [
  { title: 'Industrial Automation', path: '#services', icon: Workflow },
  { title: 'Conveyors & Material Handling', path: '#services', icon: Layers3 },
  { title: 'Smart Manufacturing', path: '#services', icon: Cpu },
  { title: 'Industrial Tools', path: '#products', icon: Wrench },
  { title: 'MRO & Services', path: '#services', icon: Settings2 },
];

const aboutCapabilities = ['Plant and assembly-line automation', 'Automated conveyor systems', 'Line and process integration', 'Customized special purpose machines', 'Engineering and design solutions', 'Fabrication and pipeline jobs', 'Installation and dismantling', 'Material handling equipment', 'MRO and industrial services', 'Industrial tools integration', 'IoT and condition monitoring', 'Machine relocation support'];

const heroSlides = [
  { src: 'automation-line-ai.jpg', alt: 'Robotic automation line assembling a vehicle body', label: 'Industrial automation' },
  { src: 'tool-in-use-ai.jpg', alt: 'Technician using a torque tool at an assembly workstation', label: 'Precision assembly' },
  { src: 'hero-overhead-crane.webp', alt: 'Industrial crane hook and lifting equipment', label: 'Material handling' },
  { src: 'hero-maintenance-pump-ai.jpg', alt: 'Technician inspecting a centrifugal pump and motor', label: 'Industrial services' },
  { src: 'gantry-machine-ai.jpg', alt: 'Cartesian gantry handling a metal component in a guarded cell', label: 'Custom automation' },
  { src: 'pick-to-light-rack.jpg', alt: 'Operator collecting a component from a pick-to-light rack', label: 'Smart kitting' },
];

export default function HomePage() {
  const location = useLocation();
  useEffect(() => {
    if (!location.hash) return;
    const id = decodeURIComponent(location.hash.slice(1));
    const timer = window.setTimeout(() => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' }), 60);
    return () => window.clearTimeout(timer);
  }, [location.hash]);
  const [slide, setSlide] = useState(0);
  const touchStart = useRef<number | null>(null);
  const liveProducts = useLiveProducts();
  const livePartners = useLivePartners();

  // Prefer live CMS records but keep the profile-backed list available if the API is empty.
  const featuredPartners = livePartners.length ? livePartners : partners;

  return <>
    <section id="top" className="home-hero home-hero--slider" aria-label="NexAge industrial engineering" onKeyDown={event => { if (event.key === 'ArrowRight') setSlide(index => (index + 1) % heroSlides.length); if (event.key === 'ArrowLeft') setSlide(index => (index - 1 + heroSlides.length) % heroSlides.length); }} onTouchStart={event => { touchStart.current = event.touches[0]?.clientX ?? null; }} onTouchEnd={event => { const end = event.changedTouches[0]?.clientX; if (touchStart.current !== null && end !== undefined && Math.abs(end - touchStart.current) > 45) setSlide(index => (index + (end < touchStart.current! ? 1 : -1) + heroSlides.length) % heroSlides.length); touchStart.current = null; }}>
      <div className="hero-slider-image" role="img" aria-label={heroSlides[slide].alt} style={{ backgroundImage: `url('/images/${heroSlides[slide].src}')` }} key={heroSlides[slide].src} />
      <div className="hero-video-shade" aria-hidden="true" />
      <div className="wrap hero-inner">
        <div className="hero-copy">
          <span className="eyebrow"><span className="eyebrow-mark" />NEXAGE INDIA PVT. LTD.</span>
          <h1>Engineering Excellence.<br /><em>Safety First.</em></h1>
          <p className="hero-lead">Industrial automation, material handling and MRO for modern manufacturing.</p>
          <p className="hero-subcopy">From engineering and system integration to installation, commissioning and ongoing support.</p>
          <div className="hero-actions">
            <a className="button button--yellow" href="#enquiry">Request a Quote <ArrowUpRight size={16} /></a>
            <a className="button button--outline-light" href="#services">Explore Services <ArrowRight size={16} /></a>
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
        {capabilities.map(({ title, path, icon: Icon }) => <a href={path} key={title} className="home-capability-link"><Icon size={20} strokeWidth={1.7} /><span>{title}</span><ArrowUpRight size={14} className="capability-open" /></a>)}
      </div>
    </section>

    <section id="about" className="section about-home about-home--simple">
      <div className="wrap about-grid">
        <div className="about-photo-wrap">
          <ImageBlock src="engineering-team-ai.jpg" alt="Engineers reviewing a conveyor design at a factory workstation" className="about-photo" />
          <div className="photo-caption"><span className="caption-line" /><span>ENGINEERING WITH PURPOSE</span></div>
        </div>
        <div className="about-copy">
          <span className="eyebrow"><span className="eyebrow-mark" />ABOUT NEXAGE</span>
          <h2>Engineering solutions shaped around the work.</h2>
          <p>NexAge India Pvt. Ltd. is a team of dynamic, qualified and experienced professionals delivering engineering solutions for industrial and precision manufacturing environments.</p>
          <p>The company profile highlights experience in plant automation, conveyor systems, line integration, customized special purpose machines, process integration, fabrication, installation, dismantling and industrial services.</p>
          <p>NexAge works collaboratively with customers to develop effective ideas, efficient processes and workable solutions, with a focus on clarity around project scope.</p>
        </div>
      </div>
      <div className="wrap">
        <div className="capability-check-grid">{aboutCapabilities.map((t, i) => <div key={t}><span>{String(i + 1).padStart(2, '0')}</span><strong>{t}</strong><Check size={16} /></div>)}</div>
      </div>
    </section>

    <section id="vision" className="section about-feature">
      <div className="wrap about-feature-grid">
        <ImageBlock src="automated-cell.webp" alt="A modern guarded industrial automation cell" />
        <div>
          <span className="eyebrow"><span className="eyebrow-mark" />OUR VISION</span>
          <h2>Be a one-stop engineering services and MRO solution.</h2>
          <p>The company’s stated vision is to be a one-stop solution for engineering services and MRO among high-technology and precision manufacturing sectors.</p>
          <div className="thin-rule" />
          <span className="eyebrow"><span className="eyebrow-mark" />OUR MISSION</span>
          <h2>Help customers achieve their business objectives.</h2>
          <p>NexAge aims to support customers through expert consultation, engineering solutions and reliable services.</p>
        </div>
      </div>
    </section>

    <section id="services" className="section solutions-home home-solutions-section">
      <div className="wrap">
        <SectionTitle kicker="SERVICES & SOLUTIONS" title="What we do for your plant." text="Engineering, automation, material handling, smart manufacturing and MRO support aligned with NexAge’s documented service portfolio." />
        <div className="solutions-grid home-solutions-grid">{solutions.map((item, i) => <SolutionCard key={item.slug} item={item} index={i} />)}</div>
      </div>
    </section>

    <section id="products" className="section featured-products home-products-section">
      <div className="wrap">
        <SectionTitle kicker="PRODUCTS & SYSTEMS" title="Equipment and systems for the job." text="NexAge-developed solutions alongside clearly identified partner products and integrated systems." />
        <div className="products-grid">{liveProducts.slice(0, 6).map(item => <ProductCard key={item.slug} item={item} />)}</div>
        <div className="partner-note"><ShieldCheck size={18} /><span>Partner product ownership and relationships are identified clearly.</span><a href="#partners">View Partners <ArrowRight size={15} /></a></div>
      </div>
    </section>

    <section id="leadership" className="section leadership-section">
      <div className="wrap leadership-grid">
        <div className="leadership-photo">
          {leadership.photo ? <ImageBlock src={leadership.photo} alt={`${leadership.name}, ${leadership.title}`} /> : <div className="leadership-monogram" role="img" aria-label={`${leadership.name} photo placeholder`}>{leadership.name.split(' ').filter((_, i, a) => i === 0 || i === a.length - 1).map(w => w[0]).join('')}</div>}
        </div>
        <div className="leadership-copy">
          <span className="eyebrow"><span className="eyebrow-mark" />LEADERSHIP</span>
          <h2>{leadership.name}</h2>
          <p className="leadership-role">{leadership.title}, NexAge India Pvt. Ltd.</p>
          {leadership.bio.length ? leadership.bio.map(text => <p key={text}>{text}</p>) : <p>Profile details for the Managing Director will be published here.</p>}
          {leadership.vision ? <blockquote className="leadership-vision">{leadership.vision}</blockquote> : <blockquote className="leadership-vision">The company’s vision is to be a one-stop solution for engineering services and MRO among high-technology and precision manufacturing sectors.</blockquote>}
        </div>
      </div>
    </section>

    <section id="clients" className="home-clients-band">
      <div className="wrap home-clients-inner">
        <div className="home-clients-copy"><span className="eyebrow"><span className="eyebrow-mark" />CLIENTS & LOCATIONS</span><h2>Industrial relationships across India.</h2><p>Client names and locations as listed in the NexAge company profile.</p></div>
        <div className="partner-logo-row home-client-logo-grid" role="list" aria-label="Selected client logos">{selectedClients.map(name => <div className="partner-logo-tile" role="listitem" key={name}><ClientLogo name={name} /></div>)}</div>
      </div>
    </section>

    <section id="partners" className="partners-band partners-band--simple">
      <div className="wrap">
        <div className="partners-band-heading">
          <div><span className="eyebrow"><span className="eyebrow-mark" />BUSINESS PARTNERS</span><h2>Trusted brands. <em>Integrated by NexAge.</em></h2><p>Partner relationships are presented according to the NexAge company profile.</p></div>
        </div>
        <div className="partner-logo-row">{featuredPartners.map(partner => <div className="partner-logo-tile" key={partner.name} title={partner.relationship}><PartnerLogo name={partner.name} /></div>)}</div>
      </div>
    </section>

    <section id="enquiry" className="section contact-layout-section">
      <div className="wrap contact-layout">
        <div className="contact-info-col">
          <span className="eyebrow"><span className="eyebrow-mark" />CONTACT NEXAGE</span>
          <h2>Let’s discuss your industrial requirement.</h2>
          <p>Tell us about the process, equipment or production challenge you need help with, or contact our team directly.</p>
          <div className="contact-method"><span><MapPin size={19} /></span><div><strong>Office</strong><p>B1/14–21, Metropolis City, Near Radisson Hotel, Rudrapur, Udham Singh Nagar, Uttarakhand – 263153</p></div></div>
          <div className="contact-method"><span><Wrench size={19} /></span><div><strong>Works</strong><p>Plot No. 62 D, Sector-4, IIE-SIDCUL, Pantnagar, Uttarakhand – 263153</p></div></div>
          <div className="contact-method"><span><Phone size={19} /></span><div><strong>Phone</strong><a href="tel:+919219586605">+91-9219586605</a><a href="tel:+919258020512">+91-9258020512</a></div></div>
          <div className="contact-method"><span><Mail size={19} /></span><div><strong>Email</strong><a href="mailto:sales@nexageindia.com">sales@nexageindia.com</a></div></div>
        </div>
        <div className="quote-form-holder"><EnquiryForm /></div>
      </div>
    </section>
  </>;
}
