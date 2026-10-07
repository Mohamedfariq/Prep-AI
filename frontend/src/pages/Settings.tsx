import { FormEvent, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, Trash2, ExternalLink, CheckCircle2, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export function Settings() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Basic Profile State
  const [form, setForm] = useState({
    branch: user?.branch || '',
    graduation_year: user?.graduation_year || 2025,
    bio: '',
    target_company: '',
  });
  const [profileLoading, setProfileLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  // Resume State
  const [resumeData, setResumeData] = useState<{
    filename: string | null;
    signedUrl: string | null;
    skills: string[];
    projects: any[];
    education: any[];
  }>({
    filename: null,
    signedUrl: null,
    skills: [],
    projects: [],
    education: [],
  });

  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Load existing profile from backend
  useEffect(() => {
    api.get('/api/candidate/profile')
      .then((res) => {
        const data = res.data;
        setForm({
          branch: data.branch || user?.branch || '',
          graduation_year: data.graduation_year || user?.graduation_year || 2025,
          bio: data.bio || '',
          target_company: data.target_company || '',
        });
        setResumeData({
          filename: data.resume_filename,
          signedUrl: data.resume_signed_url,
          skills: data.parsed_skills || [],
          projects: data.parsed_projects || [],
          education: data.parsed_education || [],
        });
      })
      .catch((err) => console.error('Failed to load profile', err))
      .finally(() => setProfileLoading(false));
  }, [user]);

  async function handleProfileSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      await api.put('/api/candidate/profile', form);
      if (form.target_company) {
        await api.post('/api/candidate/target-company', {
          company_id: form.target_company.toLowerCase(),
          company_name: form.target_company,
          is_primary: true,
        });
      }
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error('Failed to update profile', err);
    }
  }

  async function handleResumeUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadError('Only PDF resume files are accepted.');
      return;
    }

    setUploading(true);
    setUploadError(null);
    setUploadMessage('Uploading resume & parsing with AI...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post('/api/candidate/resume/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const data = res.data;
      setResumeData({
        filename: data.filename,
        signedUrl: data.signed_url,
        skills: data.parsed.skills || [],
        projects: data.parsed.projects || [],
        education: data.parsed.education || [],
      });
      setUploadMessage('Resume successfully uploaded and parsed!');
      setTimeout(() => setUploadMessage(null), 4000);
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || 'Failed to upload resume.');
    } finally {
      setUploading(false);
    }
  }

  async function handleDeleteResume() {
    if (!window.confirm('Are you sure you want to delete your resume and clear extracted data?')) return;
    try {
      await api.delete('/api/candidate/resume');
      setResumeData({
        filename: null,
        signedUrl: null,
        skills: [],
        projects: [],
        education: [],
      });
    } catch (err) {
      console.error('Failed to delete resume', err);
    }
  }

  function signOut() {
    logout();
    navigate('/login');
  }

  return (
    <div className="space-y-8 max-w-4xl pb-12">
      <section className="card p-8">
        <h1 className="text-3xl font-extrabold">Candidate Settings & Profile</h1>
        <p className="mt-2 text-[#60708d]">
          Manage your personal details, target companies, and upload your resume for automated skill extraction.
        </p>
      </section>

      {/* Candidate Profile Details */}
      <div className="soft-card p-6 space-y-6">
        <h2 className="text-xl font-bold">Academic & Target Profile</h2>
        <form className="space-y-4" onSubmit={handleProfileSubmit}>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block">
              <span className="font-semibold text-sm">Email Address</span>
              <div className="input-shell mt-1 bg-gray-50 text-gray-500">{user?.email}</div>
            </label>
            <label className="block">
              <span className="font-semibold text-sm">Full Name</span>
              <div className="input-shell mt-1 bg-gray-50 text-gray-500">{user?.name}</div>
            </label>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="block">
              <span className="font-semibold text-sm">Branch / Major</span>
              <span className="input-shell mt-1">
                <input
                  value={form.branch}
                  onChange={(e) => setForm({ ...form, branch: e.target.value })}
                  placeholder="Computer Science & Engineering"
                />
              </span>
            </label>
            <label className="block">
              <span className="font-semibold text-sm">Graduation Year</span>
              <span className="input-shell mt-1">
                <input
                  type="number"
                  value={form.graduation_year}
                  onChange={(e) => setForm({ ...form, graduation_year: Number(e.target.value) })}
                />
              </span>
            </label>
          </div>

          <label className="block">
            <span className="font-semibold text-sm">Primary Target Company</span>
            <span className="input-shell mt-1">
              <input
                value={form.target_company}
                onChange={(e) => setForm({ ...form, target_company: e.target.value })}
                placeholder="Google, Amazon, Microsoft, Uber..."
              />
            </span>
          </label>

          <label className="block">
            <span className="font-semibold text-sm">Bio / Focus Statement</span>
            <span className="input-shell mt-1">
              <textarea
                className="w-full bg-transparent outline-none resize-none h-20"
                value={form.bio}
                onChange={(e) => setForm({ ...form, bio: e.target.value })}
                placeholder="Aspiring backend engineer focusing on distributed systems and DSA..."
              />
            </span>
          </label>

          {saved && (
            <div className="flex items-center gap-2 rounded-xl bg-emerald-50 p-3 text-emerald-700 text-sm">
              <CheckCircle2 className="h-4 w-4" /> Profile changes saved.
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button className="primary-btn" type="submit">Save Profile</button>
            <button className="secondary-btn" type="button" onClick={signOut}>Logout</button>
          </div>
        </form>
      </div>

      {/* Resume Management & Parsing */}
      <div className="soft-card p-6 space-y-6">
        <div>
          <h2 className="text-xl font-bold">Resume Management (Private Object Storage)</h2>
          <p className="text-sm text-[#60708d] mt-1">
            Resumes are stored securely in Supabase Storage with expiring signed URLs. PII is redacted before AI parsing.
          </p>
        </div>

        {resumeData.filename ? (
          <div className="rounded-xl border border-line p-5 bg-white space-y-4">
            <div className="flex items-center justify-between flex-wrap gap-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-blue-50 text-blue-600 rounded-lg">
                  <FileText className="h-6 w-6" />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-[#0f172a]">{resumeData.filename}</h4>
                  <span className="text-xs text-emerald-600 font-medium flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3" /> Encrypted & Stored in Supabase
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {resumeData.signedUrl && (
                  <a
                    href={resumeData.signedUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="secondary-btn text-xs py-2 px-3 flex items-center gap-1"
                  >
                    <ExternalLink className="h-3.5 w-3.5" /> View / Download
                  </a>
                )}
                <button
                  onClick={handleDeleteResume}
                  className="p-2 text-rose-500 hover:bg-rose-50 rounded-lg transition"
                  title="Delete Resume"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Extracted Skills Preview */}
            {resumeData.skills.length > 0 && (
              <div className="border-t border-line pt-4 space-y-2">
                <h5 className="text-xs font-bold uppercase tracking-wider text-[#60708d]">
                  AI Extracted Skills ({resumeData.skills.length})
                </h5>
                <div className="flex flex-wrap gap-1.5">
                  {resumeData.skills.map((skill) => (
                    <span
                      key={skill}
                      className="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs rounded-full font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="border-2 border-dashed border-line rounded-xl p-8 text-center space-y-4 hover:border-brand transition">
            <div className="mx-auto w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center">
              <UploadCloud className="h-6 w-6" />
            </div>
            <div>
              <p className="font-semibold text-sm text-[#0f172a]">Upload your Technical Resume (PDF)</p>
              <p className="text-xs text-[#60708d] mt-1">Maximum file size: 10MB</p>
            </div>
            <div>
              <label className="primary-btn cursor-pointer inline-flex items-center gap-2">
                <UploadCloud className="h-4 w-4" />
                <span>{uploading ? 'Processing...' : 'Select PDF File'}</span>
                <input
                  type="file"
                  accept="application/pdf"
                  className="hidden"
                  disabled={uploading}
                  onChange={handleResumeUpload}
                />
              </label>
            </div>
          </div>
        )}

        {uploadMessage && (
          <div className="flex items-center gap-2 rounded-xl bg-blue-50 p-3 text-blue-700 text-sm">
            <CheckCircle2 className="h-4 w-4" /> {uploadMessage}
          </div>
        )}

        {uploadError && (
          <div className="flex items-center gap-2 rounded-xl bg-rose-50 p-3 text-rose-700 text-sm">
            <AlertCircle className="h-4 w-4" /> {uploadError}
          </div>
        )}
      </div>
    </div>
  );
}
