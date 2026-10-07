import {
  BarChart3,
  Bell,
  BookOpen,
  Bot,
  Building2,
  ChevronDown,
  ClipboardCheck,
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
import { useAuth } from '../context/AuthContext';

const navGroups = [
  {
    label: 'MAIN',
    items: [
      { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
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
    <div className="min-h-screen bg-[#f7faff]">
      <button className="fixed left-4 top-4 z-50 rounded-xl bg-white p-3 shadow-subtle lg:hidden" onClick={() => setOpen(true)} aria-label="Open navigation">
        <Menu />
      </button>
      <aside className={`fixed inset-y-0 left-0 z-40 flex w-80 flex-col border-r border-line bg-white transition-transform lg:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex h-20 items-center justify-between border-b border-line px-5">
          <Logo />
          <button className="lg:hidden" onClick={() => setOpen(false)} aria-label="Close navigation">
            <X />
          </button>
        </div>
        <nav className="flex-1 overflow-y-auto px-5 py-6">
          {navGroups.map((group) => (
            <div className="mb-8" key={group.label}>
              <p className="mb-3 px-4 text-sm font-bold tracking-wide text-[#91a0b7]">{group.label}</p>
              <div className="space-y-1">
                {group.items.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    onClick={() => setOpen(false)}
                    className={({ isActive }) =>
                      `flex items-center gap-4 rounded-xl px-4 py-3 text-lg font-medium transition ${
                        isActive ? 'bg-[#eef2ff] text-[#1d14d7]' : 'text-[#1c2b44] hover:bg-[#f5f8ff]'
                      }`
                    }
                  >
                    <item.icon className="h-5 w-5 text-[#8194b1]" />
                    <span className="flex-1">{item.label}</span>
                    {item.badge && <span className="rounded-lg bg-[#eef2ff] px-2 py-1 text-sm text-[#1d14d7]">{item.badge}</span>}
                    {item.dot && <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />}
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>
        <div className="border-t border-line p-5">
          <div className="flex items-center gap-3 rounded-2xl border border-line bg-[#f8fbff] p-3">
            <div className="relative flex h-12 w-12 items-center justify-center rounded-full bg-ink text-white">
              {user?.name?.slice(0, 2).toUpperCase() || 'FA'}
              <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-white bg-emerald-500" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate font-semibold">{user?.name || 'Candidate'}</p>
              <p className="truncate text-sm text-muted">Candidate • CSE '25</p>
            </div>
            <button onClick={signOut} aria-label="Logout">
              <LogOut className="h-5 w-5 text-[#8a9ab4]" />
            </button>
          </div>
        </div>
      </aside>

      <div className="lg:pl-80">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-line bg-white/95 px-6 backdrop-blur">
          <div className="ml-12 flex items-center gap-4 lg:ml-0">
            <h1 className="text-2xl font-extrabold">Dashboard</h1>
            <span className="hidden rounded-lg bg-[#eef4f4] px-3 py-1 text-base text-ink md:inline-flex">
              <span className="mr-2 mt-1 h-2.5 w-2.5 rounded-full bg-emerald-500" /> Adaptive Model: <b className="ml-1">Active Profile v2.4</b>
            </span>
          </div>
          <div className="flex items-center gap-4">
            <button className="hidden items-center gap-2 rounded-xl border border-[#bdcbe0] px-4 py-2 text-sm md:flex">
              <span className="text-[#9aa8bd]">Preparing for:</span>
              <span className="h-2.5 w-2.5 rounded-full bg-amber-500" />
              Amazon
              <ChevronDown className="h-4 w-4" />
            </button>
            <Search className="h-5 w-5 text-[#8194b1]" />
            <Bell className="h-5 w-5 text-[#8194b1]" />
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand text-white">FA</div>
            <span className="hidden font-medium md:inline">{user?.name?.split(' ')[0] || 'Fariq'}</span>
          </div>
        </header>
        <main className="p-5 sm:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
