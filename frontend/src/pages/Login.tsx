import { ArrowRight, Eye, LockKeyhole, Mail } from 'lucide-react';
import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthShell, OAuthPlaceholders } from '../components/AuthShell';
import { useAuth } from '../context/AuthContext';

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
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
      <h2 className="text-3xl font-extrabold tracking-tight">Welcome back, Candidate</h2>
      <p className="mt-3 text-lg leading-7 text-[#4f5667]">Enter your credentials or university SSO to access your telemetry dashboard</p>
      <div className="mt-7">
        <OAuthPlaceholders />
      </div>
      <div className="my-5 flex items-center gap-4 text-[#3d4250]">
        <span className="h-px flex-1 bg-line" />
        or continue with email
        <span className="h-px flex-1 bg-line" />
      </div>
      <form className="space-y-5" onSubmit={submit}>
        <label className="block">
          <span className="font-semibold">College or Personal Email</span>
          <span className="input-shell mt-2">
            <Mail className="h-5 w-5 text-[#566173]" />
            <input autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required placeholder="fariq.alam@campus.edu" />
          </span>
        </label>
        <label className="block">
          <span className="font-semibold">Password</span>
          <span className="input-shell mt-2">
            <LockKeyhole className="h-5 w-5 text-[#566173]" />
            <input autoComplete="current-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required placeholder="••••••••••••" />
            <Eye className="h-5 w-5 text-[#566173]" />
          </span>
        </label>
        <div className="flex items-center justify-between gap-3 text-sm font-medium">
          <label className="flex items-center gap-2 text-[#3d4250]">
            <input className="h-5 w-5 accent-brand" type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} />
            Remember device for 30 days
          </label>
          <button className="text-[#1d14d7]" type="button">Forgot password?</button>
        </div>
        {error && <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}
        <button className="primary-btn w-full text-xl" disabled={loading}>
          {loading ? 'Signing in...' : 'Sign In to PrepAI'} <ArrowRight />
        </button>
      </form>
    </AuthShell>
  );
}
