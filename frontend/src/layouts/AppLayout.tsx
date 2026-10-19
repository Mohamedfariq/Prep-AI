import {
  BarChart3,
  Bell,
  BookOpen,
  Bot,
  Building2,
  ChevronDown,
  ClipboardCheck,
  FileText,
  Gauge,
  LayoutDashboard,
  Lightbulb,
  LogOut,
  Menu,
  Search,
  Settings,
  TrendingUp,
  UserRound,
  X,
} from 'lucide-react';
import { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { Logo } from '../components/Logo';
import { ThemeToggle } from '../components/ThemeToggle';
import { useAuth } from '../context/AuthContext';

const navGroups = [
  {
    label: 'MAIN',
    items: [
      { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
      { to: '/settings', label: 'Resume & Profile', icon: FileText, badge: 'AI' },
      { to: '/companies', label: 'Companies', icon: Building2, badge: '35+' },
      { to: '/practice', label: 'Personalized Practice', icon: Lightbulb },
      { to: '/personalized-oa', label: 'Personalized OA', icon: ClipboardCheck, dot: true },
      { to: '/interview', label: 'Interview Preparation', icon: Bot },
    ],
  },
  {
    label: 'PROGRESS',
    items: [
      { to: '/skill-profile', label: 'My Skill Profile', icon: UserRound },
      { to: '/performance', label: 'Performance History', icon: Gauge },
      { to: '/recommendations', label: 'Recommendations', icon: TrendingUp, badge: 'New' },
    ],
  },
  {
    label: 'OTHER',
    items: [
      { to: '/question-bank', label: 'Question Bank', icon: BookOpen },
      { to: '/settings', label: 'Settings', icon: Settings },
    ],
  },
];

export function AppLayout() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  function signOut() {
    logout();
    navigate('/login');
  }

  return (
    <div className="min-h-screen bg-[#f7faff] text-[#1c2b44] transition-colors duration-200 dark:bg-[#0b0f19] dark:text-[#f8fafc]">
      <button
        className="fixed left-4 top-4 z-50 rounded-xl bg-white p-3 shadow-subtle dark:border dark:border-[#1e293b] dark:bg-[#111827] dark:text-white lg:hidden"
        onClick={() => setOpen(true)}
        aria-label="Open navigation"
      >
        <Menu />
      </button>

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-line bg-white transition-all duration-200 dark:border-[#1e293b] dark:bg-[#0d1424] lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-14 items-center justify-between border-b border-line px-4 dark:border-[#1e293b]">
          <Logo compact={false} />
          <button className="text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white lg:hidden" onClick={() => setOpen(false)} aria-label="Close navigation">
            <X className="h-5 w-5" />
          </button>
        </div>
        <nav className="flex-1 overflow-y-auto px-3.5 py-4">
          {navGroups.map((group) => (
            <div className="mb-4" key={group.label}>
              <p className="mb-1.5 px-3 text-[10px] font-bold uppercase tracking-wider text-[#91a0b7] dark:text-[#64748b]">{group.label}</p>
              <div className="space-y-0.5">
                {group.items.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    onClick={() => setOpen(false)}
                    className={({ isActive }) =>
                      `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                        isActive
                          ? 'bg-[#eef2ff] text-[#1d14d7] dark:bg-[#1a233d] dark:text-[#818cf8]'
                          : 'text-[#1c2b44] hover:bg-[#f5f8ff] dark:text-[#94a3b8] dark:hover:bg-[#162038] dark:hover:text-white'
                      }`
                    }
                  >
                    <item.icon className="h-4 w-4 shrink-0 text-[#8194b1] dark:text-[#64748b]" />
                    <span className="flex-1 truncate">{item.label}</span>
                    {item.badge && (
                      <span className="rounded-md bg-[#eef2ff] px-1.5 py-0.5 text-[11px] font-semibold text-[#1d14d7] dark:bg-[#201c59] dark:text-[#a5b4fc]">
                        {item.badge}
                      </span>
                    )}
                    {item.dot && <span className="h-2 w-2 rounded-full bg-emerald-500" />}
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>
        <div className="border-t border-line p-3 dark:border-[#1e293b]">
          <div className="flex items-center gap-2.5 rounded-xl border border-line bg-[#f8fbff] p-2.5 dark:border-[#1e293b] dark:bg-[#111827]">
            <div className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-ink text-xs font-bold text-white dark:bg-[#1e293b]">
              {user?.name?.slice(0, 2).toUpperCase() || 'FA'}
              <span className="absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full border-2 border-white bg-emerald-500 dark:border-[#111827]" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-semibold text-ink dark:text-white">{user?.name || 'Candidate'}</p>
              <p className="truncate text-[10px] text-muted dark:text-[#64748b]">Candidate • CSE '25</p>
            </div>
            <button onClick={signOut} aria-label="Logout" className="p-1 hover:text-red-500 dark:hover:text-red-400">
              <LogOut className="h-4 w-4 text-[#8a9ab4] dark:text-[#64748b]" />
            </button>
          </div>
        </div>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-line bg-white/95 px-4 sm:px-6 backdrop-blur transition-colors duration-200 dark:border-[#1e293b] dark:bg-[#0d1424]/95">
          <div className="ml-10 flex items-center gap-3 lg:ml-0">
            <h1 className="text-xl font-bold text-ink dark:text-white">Dashboard</h1>
            <span className="hidden rounded-full bg-[#eef4f4] px-2.5 py-0.5 text-xs text-ink dark:border dark:border-[#1e293b] dark:bg-[#131d38] dark:text-[#94a3b8] md:inline-flex">
              <span className="mr-1.5 mt-1.5 h-1.5 w-1.5 rounded-full bg-emerald-500" /> Adaptive Model: <b className="ml-1 text-ink dark:text-white">Active Profile v2.4</b>
            </span>
          </div>
          <div className="flex items-center gap-2.5 sm:gap-3.5">
            <button className="hidden items-center gap-1.5 rounded-lg border border-[#bdcbe0] px-3 py-1.5 text-xs dark:border-[#1e293b] dark:bg-[#131c31] dark:text-white md:flex">
              <span className="text-[#9aa8bd] dark:text-[#64748b]">Target:</span>
              <span className="h-2 w-2 rounded-full bg-amber-500" />
              Amazon
              <ChevronDown className="h-3.5 w-3.5" />
            </button>
            <Search className="h-4 w-4 text-[#8194b1] hover:text-slate-900 dark:text-[#94a3b8] dark:hover:text-white cursor-pointer" />
            <Bell className="h-4 w-4 text-[#8194b1] hover:text-slate-900 dark:text-[#94a3b8] dark:hover:text-white cursor-pointer" />
            
            {/* Moon-like Dark/Light Mode Toggle */}
            <ThemeToggle />

            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand text-xs font-bold text-white shadow-subtle">FA</div>
            <span className="hidden text-xs font-semibold text-ink dark:text-white md:inline">{user?.name?.split(' ')[0] || 'Fariq'}</span>
          </div>
        </header>
        <main className="p-4 sm:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

