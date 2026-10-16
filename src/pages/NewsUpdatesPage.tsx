import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { CTABand, PageIntro, SectionTitle } from '../components/Site';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');

type NewsItem = {
  id: number;
  title: string;
  slug: string;
  category: string;
  summary: string;
  content: string;
  image_url: string;
  image_alt_text: string;
  video_url: string;
  published_at: string;
};

type NewsApiResponse = NewsItem[] | { results?: NewsItem[] };

function getNewsItems(data: NewsApiResponse): NewsItem[] {
  if (Array.isArray(data)) return data;
  return Array.isArray(data.results) ? data.results : [];
}

async function fetchNews(): Promise<NewsItem[]> {
  const response = await fetch(`${API_BASE}/news/`, {
    headers: { Accept: 'application/json' },
    credentials: 'same-origin',
  });
  if (!response.ok) throw new Error('Company updates are currently unavailable.');
  const data = await response.json() as NewsApiResponse;
  return getNewsItems(data);
}

function embedUrl(rawUrl: string): string {
  if (!rawUrl) return '';
  try {
    const url = new URL(rawUrl);
    if (url.protocol !== 'https:') return '';
    const host = url.hostname.toLowerCase().replace(/^www\./, '');
    if (host === 'youtu.be') {
      const id = url.pathname.split('/').filter(Boolean)[0];
      return id ? `https://www.youtube-nocookie.com/embed/${encodeURIComponent(id)}` : '';
    }
    if (host === 'youtube.com' || host === 'm.youtube.com' || host === 'youtube-nocookie.com') {
      const id = url.searchParams.get('v') || url.pathname.match(/^\/(?:embed|shorts|live)\/([^/?]+)/)?.[1];
      return id ? `https://www.youtube-nocookie.com/embed/${encodeURIComponent(id)}` : '';
    }
    if (host === 'vimeo.com') {
      const id = url.pathname.split('/').filter(Boolean).find(part => /^\d+$/.test(part));
      return id ? `https://player.vimeo.com/video/${encodeURIComponent(id)}` : '';
    }
    if (host === 'player.vimeo.com' && url.pathname.startsWith('/video/')) return url.href;
  } catch {
    return '';
  }
  return '';
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

function NewsCard({ item, showImage = true }: { item: NewsItem; showImage?: boolean }) {
  const video = embedUrl(item.video_url);
  const paragraphs = item.content.split(/\n\s*\n/).map(part => part.trim()).filter(Boolean);

  return (
    <article className="news-card">
      {showImage && item.image_url && (
        <img
          className="news-card-image"
          src={item.image_url}
          alt={item.image_alt_text || item.title}
          loading="lazy"
          decoding="async"
        />
      )}
      <div className="news-card-body">
        <div className="news-card-meta">
          <span className="news-category">{item.category}</span>
          {formatDate(item.published_at) && <time dateTime={item.published_at}>{formatDate(item.published_at)}</time>}
        </div>
        <h3>{item.title}</h3>
        <p className="news-summary">{item.summary}</p>
        {paragraphs.length > 0 && (
          <div className="news-content">
            {paragraphs.map((paragraph, index) => <p key={index}>{paragraph}</p>)}
          </div>
        )}
        {video && (
          <div className="news-video">
            <iframe
              src={video}
              title={`Video: ${item.title}`}
              loading="lazy"
              referrerPolicy="strict-origin-when-cross-origin"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
            />
          </div>
        )}
        {item.video_url && !video && (
          <p><a href={item.video_url} target="_blank" rel="noopener noreferrer">Watch video <span aria-hidden="true">↗</span></a></p>
        )}
      </div>
    </article>
  );
}

export function LatestNewsSection() {
  const [items, setItems] = useState<NewsItem[]>([]);
  useEffect(() => {
    let active = true;
    fetchNews()
      .then(data => { if (active) setItems(data.slice(0, 3)); })
      .catch(() => { if (active) setItems([]); });
    return () => { active = false; };
  }, []);

  if (!items.length) return null;
  return (
    <section className="section news-home-section">
      <div className="wrap">
        <SectionTitle
          kicker="FROM NEXAGE"
          title="News, projects and company updates."
          text="Recent milestones, completed work and activities from the NexAge team."
          action={{ label: 'View All Updates', to: '/news' }}
        />
        <div className="news-grid">
          {items.map(item => <NewsCard key={item.id} item={item} showImage={false} />)}
        </div>
      </div>
    </section>
  );
}

export default function NewsUpdatesPage() {
  const [items, setItems] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let active = true;
    fetchNews()
      .then(data => { if (active) setItems(data); })
      .catch(() => { if (active) setFailed(true); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  return (
    <>
      <PageIntro
        eyebrow="NEWS & COMPANY ACTIVITIES"
        crumb="News & Updates"
        title="The latest from NexAge."
        text="Project completions, company achievements, exhibitions and engineering updates."
        image="industrial-integration.webp"
      />
      <section className="section news-page-section">
        <div className="wrap">
          <SectionTitle
            kicker="COMPANY JOURNAL"
            title="Progress worth sharing."
            text="News and updates published by the NexAge team."
          />
          {loading && <p className="news-state" role="status">Loading company updates…</p>}
          {!loading && failed && <p className="news-state" role="alert">Company updates are temporarily unavailable. Please try again later.</p>}
          {!loading && !failed && items.length === 0 && <p className="news-state">No company updates have been published yet.</p>}
          {!loading && !failed && items.length > 0 && (
            <div className="news-grid">
              {items.map(item => <NewsCard key={item.id} item={item} />)}
            </div>
          )}
          <div className="news-contact-link">
            <Link className="button button--black" to="/contact">Contact NexAge</Link>
          </div>
        </div>
      </section>
      <CTABand />
    </>
  );
}
