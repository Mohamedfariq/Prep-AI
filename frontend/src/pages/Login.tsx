import { ArrowRight, Eye, EyeOff, LockKeyhole, Mail } from 'lucide-react';
import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthShell, OAuthPlaceholders } from '../components/AuthShell';
import { useAuth } from '../context/AuthContext';

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password, remember);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to sign in. Check your credentials.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell>
      <h2 className="text-xl sm:text-2xl font-extrabold tracking-tight text-ink dark:text-white">Welcome back</h2>
      <p className="mt-1 text-xs sm:text-sm text-[#4f5667] dark:text-slate-400">
        Enter your credentials or university SSO to access your dashboard
      </p>

      <div className="mt-4">
        <OAuthPlaceholders />
      </div>

      <div className="my-4 flex items-center gap-3 text-xs text-[#64748b] dark:text-slate-500">
        <span className="h-px flex-1 bg-line dark:bg-[#1e293b]" />
        or continue with email
        <span className="h-px flex-1 bg-line dark:bg-[#1e293b]" />
      </div>

      <form className="space-y-3.5" onSubmit={submit}>
        <label className="block">
          <span className="text-xs font-semibold uppercase tracking-wider text-[#60708d] dark:text-slate-300">
            Email Address
          </span>
          <span className="input-shell mt-1.5 py-2 px-3 text-sm">
            <Mail className="h-4 w-4 shrink-0 text-[#64748b] dark:text-slate-400" />
            <input
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              placeholder="candidate@campus.edu"
              className="text-sm"
            />
          </span>
        </label>

        <label className="block">
          <span className="text-xs font-semibold uppercase tracking-wider text-[#60708d] dark:text-slate-300">
            Password
          </span>
          <span className="input-shell mt-1.5 py-2 px-3 text-sm">
            <LockKeyhole className="h-4 w-4 shrink-0 text-[#64748b] dark:text-slate-400" />
            <input
              autoComplete="current-password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
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

        <div className="flex items-center justify-between gap-2 text-xs font-medium pt-0.5">
          <label className="flex items-center gap-2 text-[#475569] dark:text-slate-300 cursor-pointer">
            <input
              className="h-4 w-4 rounded accent-brand"
              type="checkbox"
              checked={remember}
              onChange={(event) => setRemember(event.target.checked)}
            />
            Remember for 30 days
          </label>
          <button className="text-brand hover:underline dark:text-[#818cf8]" type="button">
            Forgot password?
          </button>
        </div>

        {error && (
          <p className="rounded-lg border border-red-200 bg-red-50 p-2.5 text-xs text-red-700 dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-400">
            {error}
          </p>
        )}

        <button className="primary-btn w-full py-2.5 text-sm font-semibold mt-1" disabled={loading}>
          <span>{loading ? 'Signing in...' : 'Sign In to PrepAI'}</span>
          <ArrowRight className="h-4 w-4" />
        </button>
      </form>
    </AuthShell>
  );
}
