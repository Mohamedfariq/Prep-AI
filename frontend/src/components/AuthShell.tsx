import { BarChart3, BrainCircuit, Github, Landmark, TerminalSquare, Zap } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { ThemeToggle } from './ThemeToggle';

export function AuthShell({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const isRegister = location.pathname.includes('register');

  return (
    <main className="prepai-bg relative flex min-h-screen items-center justify-center p-4 sm:p-6 transition-colors duration-200">
      {/* Moon / Sun toggle in top right corner of the site */}
      <div className="fixed right-5 top-5 z-50">
        <ThemeToggle />
      </div>

      <section className="grid w-full max-w-[1100px] overflow-hidden rounded-2xl bg-white transition-colors duration-200 shadow-[0_20px_50px_rgba(15,27,45,0.12)] dark:border dark:border-[#1e293b] dark:bg-[#0d1424] dark:shadow-[0_20px_50px_rgba(0,0,0,0.65)] lg:grid-cols-[1.1fr_1fr]">
        <div className="dot-grid flex flex-col justify-center p-6 sm:p-8 lg:p-10 transition-colors duration-200 dark:border-r dark:border-[#1e293b]">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand text-white shadow-subtle dark:shadow-[0_0_15px_rgba(99,102,241,0.35)]">
              <Zap className="h-5 w-5 fill-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-extrabold text-ink dark:text-white">PrepAI</h1>
                <span className="rounded-md bg-[#ddd8ff] px-2 py-0.5 text-xs font-bold tracking-wide text-[#17107c] dark:bg-[#201c59] dark:text-[#a5b4fc]">
                  INTELLIGENCE
                </span>
              </div>
              <p className="text-xs text-[#60708d] dark:text-slate-400">Engineering Campus Placement OS</p>
            </div>
          </div>

          <div className="mb-4 inline-flex w-fit items-center gap-2 rounded-full bg-[#edf4ff] px-3.5 py-1 text-xs font-semibold text-[#171bd6] dark:border dark:border-[#1e293b] dark:bg-[#131d38] dark:text-[#818cf8]">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Comprehensive Placement OS • 2024-2025 Season
          </div>

          <h2 className="text-2xl font-extrabold leading-tight tracking-tight text-ink dark:text-white sm:text-3xl">
            Master Company Placements from OAs to <span className="text-brand dark:text-[#818cf8]">Final Interviews.</span>
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-[#4f5667] dark:text-slate-300">
            Holistic company-specific intelligence covering Online Assessments, Live Coding Interviews, System Design, and Behavioral Rounds tailored for engineering candidates.
          </p>

          <div className="mt-6 space-y-3">
            <FeatureCard icon={<BarChart3 className="h-4 w-4" />} title="Company OA & Test Telemetry" badge="v4.2">
              Historical test patterns, weighted test-cases, and question distribution for 35+ top tech recruiters.
            </FeatureCard>
            <FeatureCard icon={<TerminalSquare className="h-4 w-4" />} title="Technical & System Design Interviews">
              Real-time mock interviews with adaptive AI debriefs and algorithmic problem breakdowns.
            </FeatureCard>
            <FeatureCard icon={<BrainCircuit className="h-4 w-4" />} title="Adaptive Placement Profiling">
              Real-time candidate readiness index computed against calibrated corporate hiring cutoffs.
            </FeatureCard>
          </div>
        </div>

        <div className="flex items-center justify-center p-6 sm:p-8 lg:p-10">
          <div className="w-full max-w-[420px]">
            <div className="mb-6 grid rounded-xl bg-[#e7effd] p-1 dark:border dark:border-[#1e293b] dark:bg-[#0b101f]">
              <div className="grid grid-cols-2 gap-1">
                <Link
                  className={`rounded-lg py-2 text-center text-xs font-bold transition ${
                    !isRegister
                      ? 'bg-white text-[#1d14c9] shadow-sm dark:border dark:border-[#334155] dark:bg-[#1e293b] dark:text-white'
                      : 'text-[#3d4250] hover:text-ink dark:text-[#64748b] dark:hover:text-[#94a3b8]'
                  }`}
                  to="/login"
                >
                  Sign In
                </Link>
                <Link
                  className={`rounded-lg py-2 text-center text-xs font-bold transition ${
                    isRegister
                      ? 'bg-white text-[#1d14c9] shadow-sm dark:border dark:border-[#334155] dark:bg-[#1e293b] dark:text-white'
                      : 'text-[#3d4250] hover:text-ink dark:text-[#64748b] dark:hover:text-[#94a3b8]'
                  }`}
                  to="/register"
                >
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
    <div className="flex gap-3.5 rounded-xl border border-line bg-white p-3.5 shadow-sm transition dark:border-[#1e293b] dark:bg-[#11192e]">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[#e6efff] text-brand dark:bg-[#18233f] dark:text-[#818cf8]">
        {icon}
      </div>
      <div>
        <h3 className="flex flex-wrap items-center gap-2 text-xs font-bold text-ink dark:text-[#f1f5f9]">
          {title}
          {badge && (
            <span className="rounded bg-[#e8eefc] px-1.5 py-0.5 text-[10px] font-semibold text-[#5d6472] dark:border dark:border-[#1e293b] dark:bg-[#1e293b] dark:text-[#94a3b8]">
              {badge}
            </span>
          )}
        </h3>
        <p className="mt-0.5 text-xs leading-relaxed text-[#4f5667] dark:text-slate-400">{children}</p>
      </div>
    </div>
  );
}

export function OAuthPlaceholders() {
  return (
    <div className="grid gap-2.5 sm:grid-cols-3">
      <button
        className="secondary-btn text-xs py-2 px-2.5 justify-center dark:border-[#1e293b] dark:bg-[#11192e] dark:text-slate-200 dark:hover:bg-[#16213c]"
        type="button"
      >
        <span className="font-extrabold text-[#4285f4]">G</span> Google
      </button>
      <button
        className="secondary-btn text-xs py-2 px-2.5 justify-center dark:border-[#1e293b] dark:bg-[#11192e] dark:text-slate-200 dark:hover:bg-[#16213c]"
        type="button"
      >
        <Github className="h-4 w-4" /> GitHub
      </button>
      <button
        className="secondary-btn text-xs py-2 px-2.5 justify-center dark:border-[#1e293b] dark:bg-[#11192e] dark:text-slate-200 dark:hover:bg-[#16213c]"
        type="button"
      >
        <Landmark className="h-4 w-4 text-brand dark:text-[#818cf8]" /> Campus SSO
      </button>
    </div>
  );
}
