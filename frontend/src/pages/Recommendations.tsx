import { Bookmark, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { LoadingState } from '../components/State';
import { api } from '../services/api';
import type { Recommendation } from '../types/api';

export function Recommendations() {
  const [items, setItems] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.get('/api/recommendations').then((response) => setItems(response.data || [])).finally(() => setLoading(false));
  }, []);
  async function action(id: string, type: 'save' | 'dismiss') {
    await api.post(`/api/recommendations/${id}/${type}`);
    setItems((current) => current.filter((item) => item._id !== id));
  }
  if (loading) return <LoadingState />;
  return (
    <div className="space-y-6">
      <section className="card p-8"><h1 className="text-3xl font-extrabold">Recommendations</h1><p className="mt-2 text-[#60708d]">Recommended For You, Weak Topic Practice, Company-Specific Questions, and Continue Practice.</p></section>
      <div className="grid gap-5 xl:grid-cols-2">
        {items.map((item) => (
          <article className="soft-card p-6" key={item._id}>
            <h2 className="text-xl font-bold">{item.title}</h2>
            <p className="mt-2 text-[#60708d]">{item.reason}</p>
            <div className="mt-4 flex gap-3">
              <button className="secondary-btn py-2" onClick={() => action(item._id, 'save')}><Bookmark className="h-4 w-4" /> Save</button>
              <button className="secondary-btn py-2" onClick={() => action(item._id, 'dismiss')}><X className="h-4 w-4" /> Dismiss</button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
