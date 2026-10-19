import { ArrowRight, CheckCircle2, Eye, EyeOff, LockKeyhole, Mail, UserRound } from 'lucide-react';
import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthShell, OAuthPlaceholders } from '../components/AuthShell';
import { useAuth } from '../context/AuthContext';

export function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', branch: 'Computer Science Engineering', graduation_year: 2025, password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError('');
    if (!/^(?=.*\d).{8,}$/.test(form.password)) {
      setError('Password must contain at least 8 characters and 1 number.');
      return;
    }
    setLoading(true);
    try {
      await register(form);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to create account.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell>
      <h2 className="text-xl sm:text-2xl font-extrabold tracking-tight text-ink dark:text-white">Create Account</h2>
      <p className="mt-1 text-xs sm:text-sm text-[#4f5667] dark:text-slate-400">
        Join engineering candidates preparing for top company recruitment drives
      </p>

      <div className="mt-4">
        <OAuthPlaceholders />
      </div>

      <div className="my-3.5 flex items-center gap-3 text-xs text-[#64748b] dark:text-slate-500">
        <span className="h-px flex-1 bg-line dark:bg-[#1e293b]" />
        or register with email
        <span className="h-px flex-1 bg-line dark:bg-[#1e293b]" />
      </div>

      <form className="space-y-3" onSubmit={submit}>
        <label className="block">
          <span className="text-xs font-semibold uppercase tracking-wider text-[#60708d] dark:text-slate-300">Full Name</span>
          <span className="input-shell mt-1.5 py-2 px-3 text-sm">
            <UserRound className="h-4 w-4 shrink-0 text-[#64748b] dark:text-slate-400" />
            <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required placeholder="e.g. Fariq Alam" className="text-sm" />
          </span>
        </label>

        <label className="block">
          <span className="text-xs font-semibold uppercase tracking-wider text-[#60708d] dark:text-slate-300">Email Address</span>
          <span className="input-shell mt-1.5 py-2 px-3 text-sm">
            <Mail className="h-4 w-4 shrink-0 text-[#64748b] dark:text-slate-400" />
            <input value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required type="email" placeholder="candidate@campus.edu" className="text-sm" />
          </span>
        </label>

        <div className="grid gap-3 sm:grid-cols-2">
          <label className="block">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#60708d] dark:text-slate-300">Graduation Year</span>
            <span className="input-shell mt-1.5 py-2 px-3 text-sm">
              <select value={form.graduation_year} onChange={(event) => setForm({ ...form, graduation_year: Number(event.target.value) })} className="text-sm">
                {[2024, 2025, 2026, 2027, 2028].map((year) => (
                  <option key={year} className="dark:bg-[#0b101f] dark:text-white">{year}</option>
                ))}
              </select>
            </span>
          </label>
          <label className="block">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#60708d] dark:text-slate-300">Branch / Domain</span>
            <span className="input-shell mt-1.5 py-2 px-3 text-sm">
              <input value={form.branch} onChange={(event) => setForm({ ...form, branch: event.target.value })} required className="text-sm" />
            </span>
          </label>
        </div>

        <label className="block">
          <span className="text-xs font-semibold uppercase tracking-wider text-[#60708d] dark:text-slate-300">Create Password</span>
          <span className="input-shell mt-1.5 py-2 px-3 text-sm">
            <LockKeyhole className="h-4 w-4 shrink-0 text-[#64748b] dark:text-slate-400" />
            <input
              type={showPassword ? 'text' : 'password'}
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
              required
              placeholder="••••••••••••"
              className="text-sm"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="text-[#64748b] hover:text-slate-900 dark:text-slate-400 dark:hover:text-white focus:outline-none"
              tabIndex={-1}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </span>
        </label>

        <p className="flex items-center gap-1.5 text-xs text-[#64748b] dark:text-slate-400">
          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
          <span>At least 8 characters with at least 1 number</span>
        </p>

        {error && (
          <p className="rounded-lg border border-red-200 bg-red-50 p-2.5 text-xs text-red-700 dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-400">
            {error}
          </p>
        )}

        <button className="primary-btn w-full py-2.5 text-sm font-semibold mt-1" disabled={loading}>
          <span>{loading ? 'Creating account...' : 'Create Account'}</span>
          <ArrowRight className="h-4 w-4" />
        </button>

        <p className="pt-2 text-center text-xs text-[#60708d] dark:text-slate-400">
          Already have an account?{' '}
          <Link className="font-semibold text-brand dark:text-[#818cf8] hover:underline" to="/login">
            Sign in
          </Link>
        </p>
      </form>
    </AuthShell>
  );
}
