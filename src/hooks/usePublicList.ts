import { useEffect, useState } from 'react';
import type { CatalogItem } from '../data';
import { awards as fallbackAwards, industries as fallbackIndustries, partners as fallbackPartners, products as fallbackProducts, projects as fallbackProjects, services as fallbackServices } from '../data';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');
type PublicRecord = Record<string, unknown>;

function isRecord(value: unknown): value is PublicRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function stringField(record: PublicRecord, key: string): string | undefined {
  const value = record[key];
  return typeof value === 'string' && value.trim() ? value.trim() : undefined;
}

function stringArrayField(record: PublicRecord, key: string): string[] | undefined {
  const value = record[key];
  if (!Array.isArray(value) || !value.every(item => typeof item === 'string')) return undefined;
  return value;
}

function publicRows(payload: unknown): PublicRecord[] | null {
  if (Array.isArray(payload)) return payload.filter(isRecord);
  if (isRecord(payload) && Array.isArray(payload.results)) return payload.results.filter(isRecord);
  return null;
}

function usePublicList<T>(endpoint: string, fallback: T[], mapItem: (raw: PublicRecord) => T | null): T[] {
  const [items, setItems] = useState<T[]>(fallback);
  useEffect(() => {
    let active = true;
    fetch(`${API_BASE}/${endpoint}/`, { headers: { Accept: 'application/json' } })
      .then(async response => {
        if (!response.ok) throw new Error('Catalogue API unavailable');
        const payload: unknown = await response.json();
        return publicRows(payload);
      })
      .then(rows => {
        if (!active || !rows?.length) return;
        const mapped = rows.map(mapItem).filter((item): item is T => item !== null);
        // Keep the company-profile-backed static catalogue for malformed or empty API data.
        if (mapped.length) setItems(mapped);
      })
      .catch(() => { /* Static company-profile-backed content remains available while the API is unavailable. */ });
    return () => { active = false; };
  }, [endpoint]);
  return items;
}

const productFallbackBySlug = new Map(fallbackProducts.map(item => [item.slug, item] as const));
const projectFallbackBySlug = new Map(fallbackProjects.map(item => [item.slug, item] as const));
const industryFallbackBySlug = new Map(fallbackIndustries.map(item => [item.slug, item] as const));
const serviceFallbackByName = new Map(fallbackServices.map(item => [item.title.toLowerCase(), item] as const));
const partnerFallbackByName = new Map(fallbackPartners.map(item => [item.name.toLowerCase(), item] as const));

export function useLiveProducts() {
  return usePublicList('products', fallbackProducts, (raw): CatalogItem | null => {
    const slug = stringField(raw, 'slug');
    if (!slug) return null;
    const fallback = productFallbackBySlug.get(slug);
    const ownership = stringField(raw, 'ownership');
    const ownershipTypes: Record<string, CatalogItem['type']> = {
      nexage: 'NexAge Solution', partner: 'Partner Product', integrated: 'Integrated Solution',
    };
    return {
      title: stringField(raw, 'title') || fallback?.title || 'Industrial Product',
      slug,
      path: `/products/${slug}`,
      description: stringField(raw, 'description') || fallback?.description || '',
      image: fallback?.image || stringField(raw, 'image_path') || 'automated-cell.webp',
      detailImage: fallback?.detailImage || stringField(raw, 'detail_image_path'),
      introImage: fallback?.introImage,
      type: (ownership && ownershipTypes[ownership]) || fallback?.type || 'Integrated Solution',
      category: stringField(raw, 'category_name') || fallback?.category || 'Industrial Systems',
      features: stringArrayField(raw, 'features') || fallback?.features,
    };
  });
}

export function useLiveProjects() {
  return usePublicList('projects', fallbackProjects, (raw): CatalogItem | null => {
    const slug = stringField(raw, 'slug');
    if (!slug) return null;
    const fallback = projectFallbackBySlug.get(slug);
    const challenge = stringField(raw, 'challenge');
    const solution = stringField(raw, 'solution');
    const application = stringField(raw, 'application');
    return {
      title: stringField(raw, 'title') || fallback?.title || 'Industrial Application',
      slug,
      path: `/projects/${slug}`,
      description: solution || application || challenge || fallback?.description || '',
      image: fallback?.image || stringField(raw, 'image_path') || 'assembly-line-overview.webp',
      detailImage: fallback?.detailImage || stringField(raw, 'detail_image_path'),
      introImage: fallback?.introImage,
      category: stringField(raw, 'category_name') || fallback?.category || 'Industrial Application',
      features: [],
      challenge: challenge || fallback?.challenge || '',
      solution: solution || fallback?.solution || application || fallback?.description || '',
      application: application || fallback?.application || fallback?.description || '',
      technology: stringField(raw, 'technology') || fallback?.technology || '',
      result: stringField(raw, 'result') || fallback?.result || '',
    };
  });
}

export function useLiveIndustries() {
  return usePublicList('industries', fallbackIndustries, (raw): CatalogItem | null => {
    const slug = stringField(raw, 'slug');
    if (!slug) return null;
    const fallback = industryFallbackBySlug.get(slug);
    return {
      title: stringField(raw, 'name') || fallback?.title || 'Industry',
      slug,
      path: '/industries',
      description: stringField(raw, 'description') || fallback?.description || '',
      image: fallback?.image || stringField(raw, 'image_path') || 'precision-manufacturing.webp',
    };
  });
}

export function useLiveServices() {
  return usePublicList('services', fallbackServices, (raw) => {
    const title = stringField(raw, 'title');
    if (!title) return null;
    const fallback = serviceFallbackByName.get(title.toLowerCase());
    return {
      title,
      image: fallback?.image || stringField(raw, 'image_path') || '',
      text: stringField(raw, 'description') || fallback?.text || '',
    };
  });
}

export function useLivePartners() {
  return usePublicList('partners', fallbackPartners, (raw) => {
    const name = stringField(raw, 'name');
    if (!name) return null;
    const fallback = partnerFallbackByName.get(name.toLowerCase());
    return {
      name,
      relationship: stringField(raw, 'relationship') || fallback?.relationship || '',
      text: stringField(raw, 'description') || fallback?.text || '',
      mark: fallback?.mark || '',
    };
  });
}

export function useLiveAwards() {
  return usePublicList('awards', fallbackAwards, (raw) => {
    const title = stringField(raw, 'title');
    if (!title) return null;
    return {
      title,
      period: stringField(raw, 'period') || '',
      text: stringField(raw, 'description') || 'Documented award reference listed in the company profile.',
    };
  });
}
