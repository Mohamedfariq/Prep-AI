import { ArrowRight } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { LoadingState } from '../components/State';
import { api } from '../services/api';
import type { Recommendation } from '../types/api';

export function Practice() {
  const [items, setItems] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.get('/api/recommendations').then((response) => setItems(response.data || [])).finally(() => setLoading(false));
  }, []);
  if (loading) return <LoadingState label="Generating personalized practice..." />;
  return (
    <RecommendationList title="Personalized Practice" subtitle="Problems ranked by company relevance, topic weakness, frequency, and recency." items={items} />
  );
}

export function RecommendationList({ title, subtitle, items }: { title: string; subtitle: string; items: Recommendation[] }) {
  return (
    <div className="space-y-6">
      <section className="card p-8">
        <h1 className="text-3xl font-extrabold">{title}</h1>
        <p className="mt-2 text-[#60708d]">{subtitle}</p>
      </section>
      <section className="grid gap-5 xl:grid-cols-2">
        {items.map((item) => (
          <article className="soft-card p-6" key={item._id || item.question_id}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold">{item.title}</h2>
                <p className="mt-2 text-[#60708d]">{item.reason}</p>
              </div>
              <span className="rounded-xl bg-[#eef2ff] px-3 py-2 font-semibold text-brand">{Math.round(item.score * 100)}%</span>
            </div>
            <div className="mt-4 flex flex-wrap gap-2 text-sm">
              <span className="rounded-lg bg-[#f4f7fb] px-3 py-1">{item.topic}</span>
              <span className="rounded-lg bg-[#f4f7fb] px-3 py-1">{item.difficulty}</span>
              <span className="rounded-lg bg-[#f4f7fb] px-3 py-1">Relevance {Math.round(item.company_relevance * 100)}%</span>
            </div>
            <Link className="primary-btn mt-5 py-2" to="/question-bank">Practice <ArrowRight className="h-4 w-4" /></Link>
          </article>
        ))}
      </section>
      {!items.length && <div className="soft-card p-8 text-muted">No recommendations yet. Select a target company and take a diagnostic OA.</div>}
    </div>
  );
}
