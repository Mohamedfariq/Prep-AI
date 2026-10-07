import { ArrowRight, Clock, ListChecks } from 'lucide-react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';

export function PersonalizedOA() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  async function start() {
    setLoading(true);
    const response = await api.post('/api/assessments/start', { question_count: 5, duration_minutes: 45 });
    navigate(`/personalized-oa/${response.data.assessment._id}`);
  }
  return (
    <div className="space-y-6">
      <section className="card p-8">
        <h1 className="text-3xl font-extrabold">Personalized OA</h1>
        <p className="mt-2 max-w-3xl text-[#60708d]">Start a diagnostic or adaptive assessment based on your target company, weak topics, and current readiness profile.</p>
      </section>
      <section className="grid gap-5 md:grid-cols-3">
        <div className="soft-card p-6"><ListChecks className="text-brand" /><h2 className="mt-4 text-xl font-bold">5 Questions</h2><p className="text-[#60708d]">Company-aligned diagnostic set</p></div>
        <div className="soft-card p-6"><Clock className="text-brand" /><h2 className="mt-4 text-xl font-bold">45 Minutes</h2><p className="text-[#60708d]">Timer and progress tracking</p></div>
        <div className="soft-card p-6"><h2 className="text-xl font-bold">Focus Topics</h2><p className="mt-4 text-[#60708d]">Graph, Dynamic Programming, Arrays, Strings</p></div>
      </section>
      <button className="primary-btn" onClick={start} disabled={loading}>{loading ? 'Starting...' : 'Start Assessment'} <ArrowRight /></button>
    </div>
  );
}
