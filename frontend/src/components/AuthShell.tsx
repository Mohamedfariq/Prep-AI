import { BarChart3, BrainCircuit, Building2, Github, Landmark, TerminalSquare, Zap } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

export function AuthShell({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const isRegister = location.pathname.includes('register');

  return (
    <main className="prepai-bg flex min-h-screen items-center justify-center px-6 py-10">
      <section className="grid min-h-[730px] w-full max-w-[1500px] overflow-hidden rounded-[22px] bg-white shadow-[0_28px_70px_rgba(15,27,45,0.16)] lg:grid-cols-[1.08fr_1fr]">
        <div className="dot-grid flex flex-col justify-center px-8 py-12 sm:px-14 lg:px-16">
          <div className="mb-10 flex items-center gap-4">
            <div className="flex h-[52px] w-[52px] items-center justify-center rounded-2xl bg-brand text-white shadow-subtle">
              <Zap className="h-7 w-7 fill-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-extrabold">PrepAI</h1>
                <span className="rounded-lg bg-[#ddd8ff] px-2 py-0.5 text-sm font-bold tracking-wide text-[#17107c]">INTELLIGENCE</span>
              </div>
              <p className="text-[#3e4657]">Engineering Campus Placement OS</p>
            </div>
          </div>

          <div className="mb-7 inline-flex w-fit rounded-full bg-[#edf4ff] px-10 py-2 text-center font-semibold text-[#171bd6]">
            Comprehensive Placement OS • 2024-2025 Season
          </div>

          <h2 className="max-w-[700px] text-[40px] font-extrabold leading-tight tracking-[-0.02em] text-ink sm:text-[46px]">
            Master Company Placements from OAs to <span className="text-brand">Final Interviews.</span>
          </h2>
          <p className="mt-6 max-w-[690px] text-xl leading-8 text-[#4f5667]">
            Holistic company-specific intelligence covering Online Assessments, Live Coding Interviews, System Design, and Behavioral Rounds tailored for engineering candidates.
          </p>

          <div className="mt-10 space-y-4">
            <FeatureCard icon={<BarChart3 />} title="Company OA & Test Telemetry" badge="v4.2">
              Historical test patterns, weighted test-cases, and question distribution for 35+ top tech giants and campus recruiters.
            </FeatureCard>
            <FeatureCard icon={<TerminalSquare />} title="Technical & System Design Interviews">
              Real-time mock interviews with adaptive AI debriefs, algorithmic problem breakdowns, and architectural evaluations.
            </FeatureCard>
            <FeatureCard icon={<BrainCircuit />} title="Adaptive Placement Profiling">
              Real-time candidate readiness index computed against calibrated corporate hiring cutoffs across all recruitment stages.
            </FeatureCard>
          </div>
        </div>

        <div className="flex items-center justify-center px-8 py-12 sm:px-12 lg:px-16">
          <div className="w-full max-w-[620px]">
            <div className="mb-9 grid rounded-xl bg-[#e7effd] p-1">
              <div className="grid grid-cols-2">
                <Link className={`rounded-xl py-3 text-center font-semibold ${!isRegister ? 'bg-white text-[#1d14c9] shadow-sm' : 'text-[#3d4250]'}`} to="/login">
                  Sign In
                </Link>
                <Link className={`rounded-xl py-3 text-center font-semibold ${isRegister ? 'bg-white text-[#1d14c9] shadow-sm' : 'text-[#3d4250]'}`} to="/register">
                  Sign Up
                </Link>
              </div>
            </div>
            {children}
          </div>
        </div>
      </section>
    </main>
  );
}

function FeatureCard({ icon, title, badge, children }: { icon: React.ReactNode; title: string; badge?: string; children: React.ReactNode }) {
  return (
    <div className="flex gap-5 rounded-2xl bg-white p-5 shadow-subtle">
      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-[#e6efff] text-brand">{icon}</div>
      <div>
        <h3 className="flex flex-wrap items-center gap-3 text-xl font-bold">
          {title}
          {badge && <span className="rounded-md bg-[#e8eefc] px-2 py-0.5 text-sm font-semibold text-[#5d6472]">{badge}</span>}
        </h3>
        <p className="mt-1 text-lg leading-7 text-[#4f5667]">{children}</p>
      </div>
    </div>
  );
}

export function OAuthPlaceholders() {
  return (
    <>
      <div className="grid gap-3 sm:grid-cols-3">
        <button className="secondary-btn bg-[#eef3ff]" type="button">
          <span className="font-extrabold text-[#4285f4]">G</span> Google
        </button>
        <button className="secondary-btn bg-[#eef3ff]" type="button">
          <Github className="h-5 w-5" /> GitHub
        </button>
        <button className="secondary-btn bg-[#eef3ff]" type="button">
          <Landmark className="h-5 w-5 text-brand" /> Campus SSO
        </button>
      </div>
    </>
  );
}
