import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Route, Routes, useLocation } from 'react-router-dom';
import HomePage from './pages/HomePage';
import { AboutPage, AwardsPage, ClientsPage, ContactPage, IndustriesPage, NotFoundPage, PartnersPage, PrivacyPage, ProductDetailPage, ProductsPage, ProjectDetailPage, ProjectsPage, QuotePage, ServicesPage, SolutionDetailPage, SolutionsPage, TermsPage } from './pages/ContentPages';
import SearchPage from './pages/SearchPage';
import AdminPage from './pages/AdminPage';
import NewsUpdatesPage from './pages/NewsUpdatesPage';
import { SEO, SiteFooter, SiteHeader } from './components/Site';
import './styles.css';


function RevealOnScroll() {
  const location = useLocation();
  useEffect(() => {
    // Keep the homepage visually calm: its only continuous motion is the muted industrial background video.
    if (location.pathname === '/') return;
    const nodes = document.querySelectorAll<HTMLElement>('.capability-item, .solution-card, .product-card, .project-card, .industry-card, .industry-page-card, .partner-detail-card, .client-location-row, .service-row, .award-mini, .detail-step-grid > div');
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reducedMotion || !('IntersectionObserver' in window)) return;
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -25px 0px' });
    nodes.forEach(node => { node.classList.add('reveal-on-scroll'); observer.observe(node); });
    return () => observer.disconnect();
  }, [location.pathname]);
  return null;
}

function App() {
  return <BrowserRouter><SEO /><RevealOnScroll /><Routes>
    <Route path="/admin" element={<AdminPage />} />
    <Route path="/" element={<><SiteHeader /><main id="main-content"><HomePage /></main><SiteFooter /></>} />
    <Route path="/about" element={<><SiteHeader /><main id="main-content"><AboutPage /></main><SiteFooter /></>} />
    <Route path="/solutions" element={<><SiteHeader /><main id="main-content"><SolutionsPage /></main><SiteFooter /></>} />
    <Route path="/solutions/:slug" element={<><SiteHeader /><main id="main-content"><SolutionDetailPage /></main><SiteFooter /></>} />
    <Route path="/products" element={<><SiteHeader /><main id="main-content"><ProductsPage /></main><SiteFooter /></>} />
    <Route path="/products/:slug" element={<><SiteHeader /><main id="main-content"><ProductDetailPage /></main><SiteFooter /></>} />
    <Route path="/industries" element={<><SiteHeader /><main id="main-content"><IndustriesPage /></main><SiteFooter /></>} />
    <Route path="/projects" element={<><SiteHeader /><main id="main-content"><ProjectsPage /></main><SiteFooter /></>} />
    <Route path="/projects/:slug" element={<><SiteHeader /><main id="main-content"><ProjectDetailPage /></main><SiteFooter /></>} />
    <Route path="/partners" element={<><SiteHeader /><main id="main-content"><PartnersPage /></main><SiteFooter /></>} />
    <Route path="/clients" element={<><SiteHeader /><main id="main-content"><ClientsPage /></main><SiteFooter /></>} />
    <Route path="/services" element={<><SiteHeader /><main id="main-content"><ServicesPage /></main><SiteFooter /></>} />
    <Route path="/awards" element={<><SiteHeader /><main id="main-content"><AwardsPage /></main><SiteFooter /></>} />
    <Route path="/contact" element={<><SiteHeader /><main id="main-content"><ContactPage /></main><SiteFooter /></>} />
    <Route path="/quote" element={<><SiteHeader /><main id="main-content"><QuotePage /></main><SiteFooter /></>} />
    <Route path="/search" element={<><SiteHeader /><main id="main-content"><SearchPage /></main><SiteFooter /></>} />
    <Route path="/news" element={<><SiteHeader /><main id="main-content"><NewsUpdatesPage /></main><SiteFooter /></>} />
    <Route path="/privacy" element={<><SiteHeader /><main id="main-content"><PrivacyPage /></main><SiteFooter /></>} />
    <Route path="/terms" element={<><SiteHeader /><main id="main-content"><TermsPage /></main><SiteFooter /></>} />
    <Route path="*" element={<><SiteHeader /><main id="main-content"><NotFoundPage /></main><SiteFooter /></>} />
  </Routes></BrowserRouter>;
}

ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
