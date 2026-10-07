import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export function Settings() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ branch: user?.branch || '', graduation_year: user?.graduation_year || 2025, target_company: '' });
  const [saved, setSaved] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault();
    await api.put('/api/candidate/profile', form);
    setSaved(true);
  }
  function signOut() {
    logout();
    navigate('/login');
  }
  return (
    <div className="space-y-6">
      <section className="card p-8"><h1 className="text-3xl font-extrabold">Settings</h1><p className="mt-2 text-[#60708d]">Candidate profile, target company, password change, notifications, and logout.</p></section>
      <form className="soft-card max-w-3xl space-y-5 p-6" onSubmit={submit}>
        <label className="block"><span className="font-semibold">Email</span><div className="input-shell mt-2">{user?.email}</div></label>
        <label className="block"><span className="font-semibold">Branch</span><span className="input-shell mt-2"><input value={form.branch} onChange={(e) => setForm({ ...form, branch: e.target.value })} /></span></label>
        <label className="block"><span className="font-semibold">Graduation Year</span><span className="input-shell mt-2"><input type="number" value={form.graduation_year} onChange={(e) => setForm({ ...form, graduation_year: Number(e.target.value) })} /></span></label>
        <label className="block"><span className="font-semibold">Target Company</span><span className="input-shell mt-2"><input value={form.target_company} onChange={(e) => setForm({ ...form, target_company: e.target.value })} placeholder="amazon" /></span></label>
        {saved && <p className="rounded-xl bg-emerald-50 p-3 text-emerald-700">Settings saved.</p>}
        <div className="flex gap-3"><button className="primary-btn">Save Settings</button><button className="secondary-btn" type="button" onClick={signOut}>Logout</button></div>
      </form>
    </div>
  );
}
