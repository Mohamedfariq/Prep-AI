import { ArrowRight, CheckCircle2, Eye, LockKeyhole, Mail, UserRound } from 'lucide-react';
import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthShell, OAuthPlaceholders } from '../components/AuthShell';
import { useAuth } from '../context/AuthContext';

export function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', branch: 'Computer Science Engineering', graduation_year: 2025, password: '' });
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
      <h2 className="text-3xl font-extrabold tracking-tight">Create your Candidate Account</h2>
      <p className="mt-3 text-lg leading-7 text-[#4f5667]">Join thousands of engineering students preparing for company recruitment drives</p>
      <div className="mt-7">
        <OAuthPlaceholders />
      </div>
      <div className="my-5 flex items-center gap-4 text-[#3d4250]">
        <span className="h-px flex-1 bg-line" />
        or register with email
        <span className="h-px flex-1 bg-line" />
      </div>
      <form className="space-y-4" onSubmit={submit}>
        <label className="block">
          <span className="font-semibold">Full Name</span>
          <span className="input-shell mt-2">
            <UserRound className="h-5 w-5 text-[#566173]" />
            <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required placeholder="e.g. Fariq Alam" />
          </span>
        </label>
        <label className="block">
          <span className="font-semibold">College or Personal Email</span>
          <span className="input-shell mt-2">
            <Mail className="h-5 w-5 text-[#566173]" />
            <input value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required type="email" placeholder="fariq.alam@campus.edu" />
          </span>
        </label>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block">
            <span className="font-semibold">Graduation Year</span>
            <span className="input-shell mt-2">
              <select value={form.graduation_year} onChange={(event) => setForm({ ...form, graduation_year: Number(event.target.value) })}>
                {[2024, 2025, 2026, 2027, 2028].map((year) => <option key={year}>{year}</option>)}
              </select>
            </span>
          </label>
          <label className="block">
            <span className="font-semibold">Branch / Domain</span>
            <span className="input-shell mt-2">
              <input value={form.branch} onChange={(event) => setForm({ ...form, branch: event.target.value })} required />
            </span>
          </label>
        </div>
        <label className="block">
          <span className="font-semibold">Create Password</span>
          <span className="input-shell mt-2">
            <LockKeyhole className="h-5 w-5 text-[#566173]" />
            <input type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} required placeholder="••••••••••••" />
            <Eye className="h-5 w-5 text-[#566173]" />
          </span>
        </label>
        <p className="flex items-center gap-2 text-sm text-[#3d4250]"><CheckCircle2 className="h-4 w-4 text-emerald-600" /> At least 8 characters, 1 number & 1 symbol</p>
        {error && <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}
        <button className="primary-btn w-full text-xl" disabled={loading}>
          {loading ? 'Creating account...' : 'Create Account'} <ArrowRight />
        </button>
        <p className="pt-3 text-center text-[#4f5667]">Already have an account? <Link className="font-semibold text-[#1d14d7]" to="/login">Sign in</Link></p>
      </form>
    </AuthShell>
  );
}
