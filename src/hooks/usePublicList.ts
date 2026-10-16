import { useEffect, useState } from 'react';
import type { CatalogItem } from '../data';
import { awards as fallbackAwards, industries as fallbackIndustries, partners as fallbackPartners, products as fallbackProducts, projects as fallbackProjects, services as fallbackServices } from '../data';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');
type Raw = Record<string, any>;

function usePublicList<T>(endpoint: string, fallback: T[], mapItem: (raw: Raw) => T): T[] {
  const [items, setItems] = useState<T[]>(fallback);
  useEffect(() => {
    let active = true;
    fetch(`${API_BASE}/${endpoint}/`, { headers: { Accept: 'application/json' } })
      .then(async response => { if (!response.ok) throw new Error('Catalogue API unavailable'); return response.json(); })
      .then((payload: unknown) => {
        const rows = Array.isArray(payload) ? payload : (payload && typeof payload === 'object' && 'results' in payload && Array.isArray((payload as { results: unknown }).results) ? (payload as { results: unknown[] }).results : []);
        if (active) setItems(rows.map(row => mapItem(row as Raw)));
      })
      .catch(() => { /* Static company-profile-backed content remains available while the API is unconfigured. */ });
    return () => { active = false; };
  }, [endpoint]);
  return items;
}

const productFallbackBySlug = new Map(fallbackProducts.map(p => [p.slug, p] as const));
const projectFallbackBySlug = new Map(fallbackProjects.map(p => [p.slug, p] as const));
const industryFallbackBySlug = new Map(fallbackIndustries.map(p => [p.slug, p] as const));
const serviceFallbackBySlug = new Map(fallbackServices.map(p => [p.title.toLowerCase(), p] as const));
const partnerFallbackByName = new Map(fallbackPartners.map(p => [p.name.toLowerCase(), p] as const));

export function useLiveProducts() {
  return usePublicList('products', fallbackProducts, (r): CatalogItem => {
    const slug = String(r.slug || ''); const fallback = productFallbackBySlug.get(slug);
    const ownership: Record<string, CatalogItem['type']> = { nexage: 'NexAge Solution', partner: 'Partner Product', integrated: 'Integrated Solution' };
    return { title: r.title || fallback?.title || 'Industrial Product', slug, path: `/products/${slug}`, description: r.description || fallback?.description || '', image: fallback?.image || (typeof r.image_path === 'string' ? r.image_path : 'automated-cell.webp'), detailImage: fallback?.detailImage || (typeof r.detail_image_path === 'string' ? r.detail_image_path : undefined), introImage: fallback?.introImage, type: ownership[r.ownership] || fallback?.type || 'Integrated Solution', category: r.category_name || fallback?.category || 'Industrial Systems', features: Array.isArray(r.features) ? r.features : fallback?.features };
  });
}
export function useLiveProjects() {
  return usePublicList('projects', fallbackProjects, (r): CatalogItem => {
    const slug = String(r.slug || ''); const fallback = projectFallbackBySlug.get(slug);
    return { title: r.title || fallback?.title || 'Industrial Application', slug, path: `/projects/${slug}`, description: r.solution || r.application || r.challenge || fallback?.description || '', image: fallback?.image || (typeof r.image_path === 'string' ? r.image_path : 'assembly-line-overview.webp'), detailImage: fallback?.detailImage || (typeof r.detail_image_path === 'string' ? r.detail_image_path : undefined), introImage: fallback?.introImage, category: r.category_name || fallback?.category || 'Industrial Application', features: [], challenge: r.challenge || fallback?.challenge || '', solution: r.solution || fallback?.solution || r.application || fallback?.description || '', application: r.application || fallback?.application || fallback?.description || '', technology: r.technology || fallback?.technology || '', result: r.result || fallback?.result || '' };
  });
}
export function useLiveIndustries() {
  return usePublicList('industries', fallbackIndustries, (r): CatalogItem => {
    const slug = String(r.slug || ''); const fallback = industryFallbackBySlug.get(slug);
    return { title: r.name || fallback?.title || 'Industry', slug, path: '/industries', description: r.description || fallback?.description || '', image: fallback?.image || (typeof r.image_path === 'string' ? r.image_path : 'precision-manufacturing.webp') };
  });
}
export function useLiveServices() {
  return usePublicList('services', fallbackServices, (r) => {
    const fallback = serviceFallbackBySlug.get(String(r.title || '').toLowerCase());
    return { title: r.title || fallback?.title || 'Industrial Service', image: fallback?.image || (typeof r.image_path === 'string' ? r.image_path : ''), text: r.description || fallback?.text || '' };
  });
}
export function useLivePartners() {
  return usePublicList('partners', fallbackPartners, (r) => {
    const fallback = partnerFallbackByName.get(String(r.name || '').toLowerCase());
    return { name: r.name || fallback?.name || 'Partner', relationship: r.relationship || fallback?.relationship || '', text: r.description || fallback?.text || '', mark: fallback?.mark || '' };
  });
}
export function useLiveAwards() {
  return usePublicList('awards', fallbackAwards, (r) => ({ title: r.title || 'Award', period: r.period || '', text: r.description || 'Documented award reference listed in the company profile.' }));
}
