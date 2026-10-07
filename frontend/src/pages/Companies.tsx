import { ArrowRight, Building2, Search } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { LoadingState } from '../components/State';
import { api } from '../services/api';
import type { Company } from '../types/api';

export function Companies() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [target, setTarget] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handle = setTimeout(() => {
      api.get('/api/companies', { params: { search: search || undefined } }).then((response) => {
        setCompanies(response.data.companies || []);
        setTarget(response.data.target_company);
      }).finally(() => setLoading(false));
    }, 250);
    return () => clearTimeout(handle);
  }, [search]);

  async function selectTarget(companyId: string) {
    await api.post('/api/candidate/target-company', { company_id: companyId });
    setTarget(companyId);
  }

  if (loading) return <LoadingState label="Loading company profiles..." />;

  return (
    <div className="space-y-6">
      <section className="card p-8">
        <h1 className="text-3xl font-extrabold">Companies</h1>
        <p className="mt-2 text-[#60708d]">Search company-specific OA profiles and choose the company you are preparing for.</p>
        <div className="input-shell mt-6 max-w-xl bg-white ring-1 ring-line">
          <Search className="h-5 w-5 text-muted" />
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search companies..." />
        </div>
      </section>
      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {companies.map((company) => (
          <article className="soft-card p-6" key={company.company_id}>
            <div className="flex items-start gap-4">
              <div className="grid h-14 w-14 place-items-center rounded-2xl bg-[#eef2ff] font-bold text-brand">{company.logo}</div>
              <div className="min-w-0 flex-1">
                <h2 className="text-xl font-bold">{company.name}</h2>
                <p className="mt-1 line-clamp-2 text-sm text-[#60708d]">{company.description}</p>
              </div>
            </div>
            <div className="mt-5 flex gap-3">
              <button className="secondary-btn flex-1 py-2" onClick={() => selectTarget(company.company_id)}>
                {target === company.company_id ? 'Target Selected' : 'Set Target'}
              </button>
              <Link className="primary-btn py-2" to={`/companies/${company.company_id}`}>
                View <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </article>
        ))}
      </section>
      {!companies.length && <div className="soft-card p-8 text-muted">No companies found. Seed the backend from the dataset using <code>/api/admin/seed</code>.</div>}
    </div>
  );
}
