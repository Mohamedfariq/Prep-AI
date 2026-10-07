import { ArrowRight, BarChart3, ClipboardCheck, Flame, PlayCircle, PieChart, ShieldCheck } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { MetricCard } from '../components/MetricCard';
import { EmptyState, LoadingState } from '../components/State';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import type { CandidateProfile, Recommendation, SkillRow } from '../types/api';

export function Dashboard() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [skills, setSkills] = useState<SkillRow[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/api/candidate/profile'),
      api.get('/api/candidate/skill-profile'),
      api.get('/api/recommendations').catch(() => ({ data: [] })),
    ])
      .then(([profileResponse, skillResponse, recResponse]) => {
        setProfile(profileResponse.data);
        setSkills(skillResponse.data.skills || []);
        setRecommendations(recResponse.data || []);
      })
      .finally(() => setLoading(false));
  }, []);

  const hasHistory = Boolean(profile?.questions_attempted);
  const mastery = hasHistory ? Math.round(profile?.overall_mastery || averageMastery(skills)) : 0;
  const topSkills = useMemo(() => skills.slice().sort((a, b) => b.mastery_probability - a.mastery_probability).slice(0, 7), [skills]);
  const weakSkills = useMemo(() => skills.slice().sort((a, b) => a.mastery_probability - b.mastery_probability).slice(0, 3), [skills]);

  if (loading) return <LoadingState label="Loading your placement intelligence dashboard..." />;

  if (!hasHistory) {
    return (
      <div className="space-y-6">
        <Hero name={user?.name || 'Candidate'} mastery={0} cold />
        <EmptyState
          title="Complete your diagnostic assessment to build your initial skill profile."
          body="PrepAI will use your target company, topic performance, and first assessment attempt to initialize BKT mastery estimates and generate recommendations."
          action={<Link className="primary-btn" to="/personalized-oa">Take Diagnostic OA <ArrowRight /></Link>}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Hero name={user?.name || 'Candidate'} mastery={mastery} />
      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Overall Mastery" value={`${mastery}%`} icon={<BarChart3 />} note={<><span className="text-emerald-600">↑ +8%</span> vs. previous month across 8 domains</>} />
        <MetricCard label="Questions Solved" value={`${profile?.questions_solved || 0}`} icon={<ShieldCheck />} note={<><span className="text-blue-700">↑ this week</span> Target pace: 20 questions/wk</>} />
        <MetricCard label="OA Performance" value={`${Math.round(profile?.accuracy || 0)}%`} icon={<PieChart />} note={<><span className="text-emerald-600">↑ improvement</span> Based on recent attempts</>} />
        <MetricCard label="Current Streak" value={`${profile?.current_streak || 0} days`} icon={<Flame />} note={<span className="text-[#8a9ab4]">Keep practicing to retain retention</span>} />
      </section>
      <section className="page-grid">
        <div className="soft-card p-8">
          <div className="flex flex-wrap items-start justify-between gap-4 border-b border-line pb-6">
            <div>
              <h2 className="text-2xl font-bold">Your Skill Profile</h2>
              <p className="text-[#60708d]">Topic mastery estimated from your recent performance & problem submissions</p>
            </div>
            <div className="flex gap-5 text-sm text-[#536380]">
              <Legend color="bg-emerald-500" label="Strong (≥70%)" />
              <Legend color="bg-amber-500" label="Developing (50-69%)" />
              <Legend color="bg-rose-500" label="Needs Attention (<50%)" />
            </div>
          </div>
          <div className="mt-6 space-y-5">
            {topSkills.map((skill) => <SkillBar key={skill.topic} skill={skill} />)}
          </div>
          <div className="mt-6 border-t border-line pt-5 text-sm text-[#60708d]">
            Based on {profile?.questions_attempted || 0} evaluation test cases analyzed
            <Link className="float-right font-semibold text-[#1d14d7]" to="/skill-profile">View Full Skill Profile →</Link>
          </div>
        </div>
        <aside className="soft-card p-8">
          <div className="border-b border-line pb-5">
            <h2 className="text-2xl font-bold">Focus Areas</h2>
            <p className="text-[#60708d]">Topics impacting your target OA readiness most</p>
          </div>
          <div className="mt-5 space-y-4">
            {weakSkills.map((skill, index) => <FocusCard key={skill.topic} skill={skill} index={index} />)}
          </div>
          <Link className="secondary-btn mt-8 w-full border-[#b8c6ff] bg-[#eef2ff] text-[#1d14d7]" to="/practice">
            <PlayCircle className="h-5 w-5" /> Practice Weak Topics
          </Link>
        </aside>
      </section>
      <section className="grid gap-5 xl:grid-cols-2">
        <div className="soft-card p-6">
          <h2 className="text-xl font-bold">Performance Trend</h2>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topSkills.map((s) => ({ topic: s.topic, mastery: Math.round(s.mastery_probability * 100) }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5edf7" />
                <XAxis dataKey="topic" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="mastery" fill="#5244e9" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="soft-card p-6">
          <h2 className="text-xl font-bold">Personalized Recommendations</h2>
          <div className="mt-4 space-y-3">
            {recommendations.slice(0, 4).map((item) => (
              <div className="rounded-xl border border-line p-4" key={item._id || item.question_id}>
                <div className="font-semibold">{item.title}</div>
                <p className="mt-1 text-sm text-[#60708d]">{item.reason}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

function Hero({ name, mastery, cold = false }: { name: string; mastery: number; cold?: boolean }) {
  return (
    <section className="card p-8">
      <div className="grid gap-6 lg:grid-cols-[1fr_440px]">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <span className="status-pill border-emerald-200 bg-emerald-50 text-emerald-700">Personalized Learning Track</span>
            <span className="text-[#8a9ab4]">• Updated recently</span>
          </div>
          <h1 className="mt-4 text-4xl font-extrabold tracking-[-0.03em]">Good evening, {name.split(' ')[0]} 👋</h1>
          <p className="mt-3 max-w-3xl text-lg leading-8 text-[#52627f]">
            {cold
              ? 'Start with a diagnostic OA so PrepAI can estimate topic mastery and prepare your first company-specific plan.'
              : "Continue your personalized placement preparation. Your custom roadmap adapts to company OA patterns and your latest performance."}
          </p>
          <div className="mt-6 flex flex-wrap gap-4">
            <Link className="primary-btn" to="/practice"><PlayCircle className="h-5 w-5" /> Start Personalized Practice</Link>
            <Link className="secondary-btn" to="/personalized-oa"><ClipboardCheck className="h-5 w-5" /> Take Diagnostic OA</Link>
          </div>
        </div>
        <div className="flex items-center gap-6 rounded-2xl border border-line bg-[#f8fbff] p-6">
          <div className="grid h-24 w-24 place-items-center rounded-full border-[8px] border-brand text-center">
            <div><div className="text-2xl font-extrabold">{mastery}%</div><div className="text-xs text-[#52627f]">READINESS</div></div>
          </div>
          <div>
            <div className="font-bold">Amazon SDE Prep <span className="ml-2 rounded-md bg-amber-100 px-2 py-1 text-sm text-amber-700">Target</span></div>
            <p className="mt-2 text-[#52627f]">Estimated OA clearing threshold: 75%</p>
            <Link className="mt-3 inline-flex items-center gap-2 font-semibold text-[#1d14d7]" to="/companies/amazon">+4% needed for safe cutoff <ArrowRight className="h-4 w-4" /></Link>
          </div>
        </div>
      </div>
    </section>
  );
}

function averageMastery(skills: SkillRow[]) {
  if (!skills.length) return 0;
  return Math.round((skills.reduce((sum, item) => sum + item.mastery_probability, 0) / skills.length) * 100);
}

function Legend({ color, label }: { color: string; label: string }) {
  return <span className="flex items-center gap-2"><span className={`h-2 w-2 rounded-full ${color}`} /> {label}</span>;
}

function SkillBar({ skill }: { skill: SkillRow }) {
  const value = Math.round(skill.mastery_probability * 100);
  const color = value >= 70 ? 'bg-emerald-500' : value >= 50 ? 'bg-amber-500' : 'bg-rose-500';
  const label = value >= 70 ? 'Strong' : value >= 50 ? 'Developing' : 'Needs Attention';
  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3">
        <div className="font-medium">{skill.topic} <span className={`ml-2 rounded-md border px-2 py-1 text-sm ${value >= 70 ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : value >= 50 ? 'border-amber-200 bg-amber-50 text-amber-700' : 'border-rose-200 bg-rose-50 text-rose-700'}`}>{label}</span></div>
        <div className="font-semibold">{value}%</div>
      </div>
      <div className="h-2.5 rounded-full bg-[#eef2f7]"><div className={`h-full rounded-full ${color}`} style={{ width: `${value}%` }} /></div>
    </div>
  );
}

function FocusCard({ skill, index }: { skill: SkillRow; index: number }) {
  const value = Math.round(skill.mastery_probability * 100);
  const tone = index === 0 ? 'border-rose-200 bg-rose-50 text-rose-700' : index === 1 ? 'border-amber-200 bg-amber-50 text-amber-700' : 'border-line bg-[#f8fbff] text-[#1c2b44]';
  return (
    <div className={`rounded-2xl border p-4 ${tone}`}>
      <div className="flex justify-between font-semibold"><span>{index + 1}. {skill.topic}</span><span>{value}%</span></div>
      <div className="mt-2 flex justify-between text-sm"><span>{value < 50 ? 'Needs improvement' : 'Developing'}</span><span>{Math.max(3, 12 - index * 3)} questions recommended</span></div>
      <div className="mt-3 h-2 rounded-full bg-white/70"><div className="h-full rounded-full bg-current" style={{ width: `${value}%` }} /></div>
    </div>
  );
}
