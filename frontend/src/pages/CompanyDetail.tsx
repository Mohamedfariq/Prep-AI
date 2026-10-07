import { ArrowRight, Building2 } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import { LoadingState } from '../components/State';
import { api } from '../services/api';

export function CompanyDetail() {
  const { companyId } = useParams();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/api/companies/${companyId}`).then((response) => setData(response.data)).finally(() => setLoading(false));
  }, [companyId]);

  const topics = useMemo(() => {
    const topicProfile = data?.oa_profile?.topic_profile || {};
    return Object.entries(topicProfile)
      .map(([topic, value]: any) => ({ topic, count: value.count || 0 }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8);
  }, [data]);

  const difficulty = useMemo(() => {
    const profile = data?.oa_profile?.difficulty_profile || {};
    return ['Easy', 'Medium', 'Hard'].map((name) => ({ name, value: profile[name]?.count || 0 }));
  }, [data]);

  if (loading) return <LoadingState label="Loading company OA profile..." />;
  if (!data?.company) return <div className="soft-card p-8 text-muted">Company profile not found.</div>;

  return (
    <div className="space-y-6">
      <section className="card p-8">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="grid h-16 w-16 place-items-center rounded-2xl bg-[#eef2ff] text-xl font-bold text-brand">{data.company.logo}</div>
            <div>
              <h1 className="text-3xl font-extrabold">{data.company.name} Preparation</h1>
              <p className="mt-1 text-[#60708d]">{data.company.description}</p>
            </div>
          </div>
          <Link className="primary-btn" to="/personalized-oa">Start Preparation <ArrowRight /></Link>
        </div>
      </section>
      <section className="grid gap-5 md:grid-cols-4">
        <Stat label="Total Questions" value={data.oa_profile?.total_questions || 0} />
        <Stat label="Unique Questions" value={data.oa_profile?.unique_questions || 0} />
        <Stat label="Mean Frequency" value={`${data.oa_profile?.frequency_profile?.mean || 0}%`} />
        <Stat label="Mean Acceptance" value={`${data.oa_profile?.acceptance_profile?.mean || 0}%`} />
      </section>
      <section className="grid gap-5 xl:grid-cols-[1fr_420px]">
        <div className="soft-card p-6">
          <h2 className="text-2xl font-bold">Most Frequent Topics</h2>
          <div className="mt-5 space-y-4">
            {topics.map((item) => (
              <div key={item.topic}>
                <div className="mb-2 flex justify-between font-medium"><span>{item.topic}</span><span>{item.count}</span></div>
                <div className="h-2.5 rounded-full bg-[#eef2f7]"><div className="h-full rounded-full bg-brand" style={{ width: `${Math.min(100, item.count)}%` }} /></div>
              </div>
            ))}
          </div>
        </div>
        <div className="soft-card p-6">
          <h2 className="text-2xl font-bold">Difficulty Distribution</h2>
          <div className="h-72">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={difficulty} dataKey="value" nameKey="name" outerRadius={100} label>
                  {difficulty.map((_, index) => <Cell key={index} fill={['#10b981', '#f59e0b', '#f43f5e'][index]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return <div className="soft-card p-5"><p className="text-[#60708d]">{label}</p><p className="mt-3 text-3xl font-extrabold">{value}</p></div>;
}
