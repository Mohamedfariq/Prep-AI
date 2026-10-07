import { useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { LoadingState } from '../components/State';
import { api } from '../services/api';

export function Performance() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.get('/api/candidate/performance').then((response) => setData(response.data)).finally(() => setLoading(false));
  }, []);
  if (loading) return <LoadingState />;
  const topicData = Object.entries(data.topic_accuracy || {}).map(([topic, value]: any) => ({ topic, accuracy: value.attempts ? Math.round(value.correct / value.attempts * 100) : 0 }));
  return (
    <div className="space-y-6">
      <section className="card p-8"><h1 className="text-3xl font-extrabold">Performance History</h1><p className="mt-2 text-[#60708d]">Performance over time, topic accuracy, difficulty accuracy, and recent attempts.</p></section>
      <section className="grid gap-5 md:grid-cols-3">
        <Stat label="Attempts" value={data.summary.attempts} />
        <Stat label="Correct" value={data.summary.correct} />
        <Stat label="Accuracy" value={`${data.summary.accuracy}%`} />
      </section>
      <div className="soft-card p-6">
        <h2 className="text-xl font-bold">Topic Accuracy</h2>
        <div className="mt-4 h-72">
          <ResponsiveContainer>
            <BarChart data={topicData}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="topic" /><YAxis /><Tooltip /><Bar dataKey="accuracy" fill="#5244e9" radius={[8, 8, 0, 0]} /></BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return <div className="soft-card p-5"><p className="text-[#60708d]">{label}</p><p className="mt-3 text-3xl font-extrabold">{value}</p></div>;
}
