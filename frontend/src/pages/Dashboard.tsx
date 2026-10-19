import { ArrowRight, BarChart3, CheckCircle2, ClipboardCheck, ExternalLink, FileText, Flame, PlayCircle, PieChart, ShieldCheck } from 'lucide-react';
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

  const resumeBanner = (
    <div className="card p-4 sm:p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-gradient-to-r from-blue-50/70 to-indigo-50/50 border border-blue-100 dark:from-[#11192e] dark:to-[#16223e] dark:border-[#1e293b]">
      <div className="flex items-center gap-3.5">
        <div className="p-2.5 bg-brand/10 text-brand rounded-xl">
          <FileText className="h-5 w-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-base text-slate-800 dark:text-white">
              {profile?.resume_filename ? profile.resume_filename : "Technical Resume (PDF)"}
            </h3>
            {profile?.resume_filename ? (
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border dark:border-emerald-800 font-semibold flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3" /> Stored in Supabase
              </span>
            ) : (
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 dark:border dark:border-amber-800 font-semibold">
                Not Uploaded Yet
              </span>
            )}
          </div>
          <p className="text-xs text-[#60708d] dark:text-slate-400 mt-0.5">
            {profile?.parsed_skills && profile.parsed_skills.length > 0
              ? `Extracted ${profile.parsed_skills.length} skills with AI: ${profile.parsed_skills.slice(0, 7).join(", ")}${profile.parsed_skills.length > 7 ? "..." : ""}`
              : "Upload your resume in PDF format to auto-extract technical skills via local Qwen2.5 AI and seed your preparation plan."}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2.5 w-full md:w-auto">
        {profile?.resume_signed_url && (
          <a
            href={profile.resume_signed_url}
            target="_blank"
            rel="noreferrer"
            className="secondary-btn text-xs py-1.5 px-3 flex items-center gap-1.5"
          >
            <ExternalLink className="h-3.5 w-3.5" /> View Resume
          </a>
        )}
        <Link to="/settings" className="primary-btn text-xs py-1.5 px-3.5 whitespace-nowrap">
          {profile?.resume_filename ? "Manage Resume" : "Upload Resume →"}
        </Link>
      </div>
    </div>
  );

  if (!hasHistory) {
    return (
      <div className="space-y-4 sm:space-y-5">
        <Hero name={user?.name || 'Candidate'} mastery={0} cold />
        {resumeBanner}
        <EmptyState
          title="Complete your diagnostic assessment to build your initial skill profile."
          body="PrepAI will use your target company, topic performance, and first assessment attempt to initialize BKT mastery estimates and generate recommendations."
          action={<Link className="primary-btn text-sm py-2 px-4" to="/skill-profile">Take Diagnostic Assessment <ArrowRight className="h-4 w-4" /></Link>}
        />
      </div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-5">
      <Hero name={user?.name || 'Candidate'} mastery={mastery} />
      {resumeBanner}
      <section className="grid gap-3.5 sm:gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Overall Mastery" value={`${mastery}%`} icon={<BarChart3 className="h-4 w-4" />} note={<><span className="text-emerald-600 dark:text-emerald-400">↑ +8%</span> vs. previous month across 8 domains</>} />
        <MetricCard label="Questions Solved" value={`${profile?.questions_solved || 0}`} icon={<ShieldCheck className="h-4 w-4" />} note={<><span className="text-blue-700 dark:text-blue-400">↑ this week</span> Target pace: 20 questions/wk</>} />
        <MetricCard label="OA Performance" value={`${Math.round(profile?.accuracy || 0)}%`} icon={<PieChart className="h-4 w-4" />} note={<><span className="text-emerald-600 dark:text-emerald-400">↑ improvement</span> Based on recent attempts</>} />
        <MetricCard label="Current Streak" value={`${profile?.current_streak || 0} days`} icon={<Flame className="h-4 w-4" />} note={<span className="text-[#8a9ab4] dark:text-slate-400">Keep practicing to retain retention</span>} />
      </section>
      <section className="page-grid">
        <div className="soft-card p-5 sm:p-6">
          <div className="flex flex-wrap items-start justify-between gap-3 border-b border-line dark:border-[#1e293b] pb-4">
            <div>
              <h2 className="text-xl font-bold text-ink dark:text-white">Your Skill Profile</h2>
              <p className="text-xs text-[#60708d] dark:text-slate-400">Topic mastery estimated from your recent performance & problem submissions</p>
            </div>
            <div className="flex gap-3.5 text-xs text-[#536380] dark:text-slate-400">
              <Legend color="bg-emerald-500" label="Strong (≥70%)" />
              <Legend color="bg-amber-500" label="Developing (50-69%)" />
              <Legend color="bg-rose-500" label="Needs Attention (<50%)" />
            </div>
          </div>
          <div className="mt-4 space-y-3.5">
            {topSkills.map((skill) => <SkillBar key={skill.topic} skill={skill} />)}
          </div>
          <div className="mt-5 border-t border-line dark:border-[#1e293b] pt-3 text-xs text-[#60708d] dark:text-slate-400">
            Based on {profile?.questions_attempted || 0} evaluation test cases analyzed
            <Link className="float-right font-semibold text-brand dark:text-[#818cf8]" to="/skill-profile">View Full Skill Profile →</Link>
          </div>
        </div>
        <aside className="soft-card p-5 sm:p-6">
          <div className="border-b border-line dark:border-[#1e293b] pb-4">
            <h2 className="text-xl font-bold text-ink dark:text-white">Focus Areas</h2>
            <p className="text-xs text-[#60708d] dark:text-slate-400">Topics impacting your target OA readiness most</p>
          </div>
          <div className="mt-4 space-y-3">
            {weakSkills.map((skill, index) => <FocusCard key={skill.topic} skill={skill} index={index} />)}
          </div>
          <Link className="secondary-btn mt-5 w-full text-xs py-2 dark:border-[#1e293b] dark:bg-[#162038] dark:text-[#818cf8]" to="/practice">
            <PlayCircle className="h-4 w-4" /> Practice Weak Topics
          </Link>
        </aside>
      </section>
      <section className="grid gap-4 xl:grid-cols-2">
        <div className="soft-card p-5">
          <h2 className="text-lg font-bold text-ink dark:text-white">Performance Trend</h2>
          <div className="mt-3 h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topSkills.map((s) => ({ topic: s.topic, mastery: Math.round(s.mastery_probability * 100) }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5edf7" className="dark:opacity-10" />
                <XAxis dataKey="topic" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: '#11192e', borderColor: '#1e293b', borderRadius: '8px', color: '#fff' }} />
                <Bar dataKey="mastery" fill="#5244e9" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="soft-card p-5">
          <h2 className="text-lg font-bold text-ink dark:text-white">Personalized Recommendations</h2>
          <div className="mt-3 space-y-2.5">
            {recommendations.slice(0, 4).map((item) => (
              <div className="rounded-lg border border-line dark:border-[#1e293b] dark:bg-[#0b101f] p-3" key={item._id || item.question_id}>
                <div className="font-semibold text-xs sm:text-sm text-ink dark:text-white">{item.title}</div>
                <p className="mt-0.5 text-xs text-[#60708d] dark:text-slate-400">{item.reason}</p>
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
    <section className="card p-5 sm:p-6">
      <div className="grid gap-5 lg:grid-cols-[1fr_360px] items-center">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <span className="status-pill border-emerald-200 bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:border-emerald-800 dark:text-emerald-300">
              Personalized Learning Track
            </span>
            <span className="text-xs text-[#8a9ab4] dark:text-slate-400">• Updated recently</span>
          </div>
          <h1 className="mt-3 text-2xl sm:text-3xl font-extrabold tracking-[-0.02em] text-ink dark:text-white">
            Good evening, {name.split(' ')[0]} 👋
          </h1>
          <p className="mt-2 max-w-2xl text-xs sm:text-sm leading-relaxed text-[#52627f] dark:text-slate-400">
            {cold
              ? 'Start with a diagnostic OA so PrepAI can estimate topic mastery and prepare your first company-specific plan.'
              : "Continue your personalized placement preparation. Your custom roadmap adapts to company OA patterns and your latest performance."}
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <Link className="primary-btn text-xs py-2 px-3.5" to="/practice">
              <PlayCircle className="h-4 w-4" /> Start Practice
            </Link>
            <Link className="secondary-btn text-xs py-2 px-3.5" to="/personalized-oa">
              <ClipboardCheck className="h-4 w-4" /> Take Diagnostic OA
            </Link>
          </div>
        </div>

        {/* Readiness Widget: Dark mode & compact size */}
        <div className="flex items-center gap-4 rounded-xl border border-line bg-[#f8fbff] dark:bg-[#0e1628] dark:border-[#1e293b] p-4">
          <div className="grid h-16 w-16 shrink-0 place-items-center rounded-full border-[5px] border-brand text-center">
            <div>
              <div className="text-lg font-extrabold text-ink dark:text-white leading-none">{mastery}%</div>
              <div className="text-[9px] font-bold text-[#52627f] dark:text-slate-400 uppercase mt-0.5">READINESS</div>
            </div>
          </div>
          <div className="min-w-0">
            <div className="font-bold text-xs sm:text-sm text-ink dark:text-white flex items-center gap-1.5 flex-wrap">
              <span>Amazon SDE Prep</span>
              <span className="rounded-md bg-amber-100 dark:bg-amber-950/60 dark:text-amber-300 dark:border dark:border-amber-800 px-1.5 py-0.5 text-[10px] text-amber-700 font-semibold">
                Target
              </span>
            </div>
            <p className="mt-1 text-xs text-[#52627f] dark:text-slate-400">Estimated OA clearing threshold: 75%</p>
            <Link className="mt-1.5 inline-flex items-center gap-1 text-xs font-semibold text-brand dark:text-[#818cf8] hover:underline" to="/companies/amazon">
              +4% needed for safe cutoff <ArrowRight className="h-3.5 w-3.5" />
            </Link>
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
  return <span className="flex items-center gap-1.5"><span className={`h-2 w-2 rounded-full ${color}`} /> {label}</span>;
}

function SkillBar({ skill }: { skill: SkillRow }) {
  const value = Math.round(skill.mastery_probability * 100);
  const color = value >= 70 ? 'bg-emerald-500' : value >= 50 ? 'bg-amber-500' : 'bg-rose-500';
  const label = value >= 70 ? 'Strong' : value >= 50 ? 'Developing' : 'Needs Attention';
  return (
    <div>
      <div className="mb-1 flex items-center justify-between gap-3 text-xs">
        <div className="font-medium text-ink dark:text-white">
          {skill.topic}{' '}
          <span className={`ml-1.5 rounded-md border px-1.5 py-0.5 text-[10px] ${
            value >= 70
              ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:border-emerald-800 dark:text-emerald-300'
              : value >= 50
              ? 'border-amber-200 bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:border-amber-800 dark:text-amber-300'
              : 'border-rose-200 bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:border-rose-900 dark:text-rose-300'
          }`}>
            {label}
          </span>
        </div>
        <div className="font-semibold text-ink dark:text-white">{value}%</div>
      </div>
      <div className="h-2 rounded-full bg-[#eef2f7] dark:bg-[#1e293b]">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

function FocusCard({ skill, index }: { skill: SkillRow; index: number }) {
  const value = Math.round(skill.mastery_probability * 100);
  const tone =
    index === 0
      ? 'border-rose-200 bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:border-rose-900 dark:text-rose-300'
      : index === 1
      ? 'border-amber-200 bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:border-amber-900 dark:text-amber-300'
      : 'border-line dark:border-[#1e293b] bg-[#f8fbff] dark:bg-[#0e1628] text-[#1c2b44] dark:text-slate-200';
  return (
    <div className={`rounded-xl border p-3 ${tone}`}>
      <div className="flex justify-between font-semibold text-xs sm:text-sm">
        <span>{index + 1}. {skill.topic}</span>
        <span>{value}%</span>
      </div>
      <div className="mt-1 flex justify-between text-xs opacity-90">
        <span>{value < 50 ? 'Needs improvement' : 'Developing'}</span>
        <span>{Math.max(3, 12 - index * 3)} questions recommended</span>
      </div>
      <div className="mt-2 h-1.5 rounded-full bg-white/70 dark:bg-white/20">
        <div className="h-full rounded-full bg-current" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

