import { ArrowLeft, ArrowRight, ArrowUpRight, Building2, CheckCircle2, Filter, Search } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { LoadingState } from '../components/State';
import { api } from '../services/api';
import type { Company } from '../types/api';

const ALPHABETS = ['ALL', '#', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];

export function Companies() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [target, setTarget] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [selectedLetter, setSelectedLetter] = useState('ALL');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const pageSize = 36;

  // Reset page when search or letter changes
  useEffect(() => {
    setPage(1);
  }, [search, selectedLetter]);

  useEffect(() => {
    setLoading(true);
    const handle = setTimeout(() => {
      api.get('/api/companies', {
        params: {
          search: search || undefined,
          letter: selectedLetter !== 'ALL' ? selectedLetter : undefined,
          limit: 1000,
        },
      })
        .then((response) => {
          setCompanies(response.data.companies || []);
          setTarget(response.data.target_company);
        })
        .catch((err) => console.error('Failed to load companies', err))
        .finally(() => setLoading(false));
    }, 200);

    return () => clearTimeout(handle);
  }, [search, selectedLetter]);

  async function selectTarget(companyId: string, companyName: string) {
    try {
      await api.post('/api/candidate/target-company', {
        company_id: companyId,
        company_name: companyName,
        is_primary: true,
      });
      setTarget(companyId);
    } catch (err) {
      console.error('Failed to set target company', err);
    }
  }

  const totalPages = Math.ceil(companies.length / pageSize) || 1;
  const paginatedCompanies = companies.slice((page - 1) * pageSize, page * pageSize);
  const startItem = companies.length === 0 ? 0 : (page - 1) * pageSize + 1;
  const endItem = Math.min(page * pageSize, companies.length);

  return (
    <div className="space-y-4 max-w-7xl pb-16">
      <section className="card p-5 sm:p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-extrabold text-ink dark:text-white">Company Intelligence & OA Profiles</h1>
            <p className="mt-1 text-xs sm:text-sm text-[#60708d] dark:text-slate-400">
              Explore hiring patterns, assessment frequency, and interview question banks across all <b>{companies.length}</b> companies.
            </p>
          </div>
          <div className="flex items-center gap-2 self-start md:self-auto">
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-brand/10 text-brand dark:bg-brand/20 dark:text-[#818cf8]">
              {companies.length} Companies Indexed
            </span>
          </div>
        </div>

        {/* Search Bar */}
        <div className="mt-4 input-shell max-w-xl dark:bg-[#0b101f] dark:ring-1 dark:ring-[#1e293b]">
          <Search className="h-4 w-4 text-muted dark:text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search companies by name (e.g. Google, Amazon, Microsoft, Uber)..."
          />
        </div>

        {/* A-Z Alphabet Quick Bar */}
        <div className="mt-4 pt-3 border-t border-line dark:border-[#1e293b]">
          <div className="text-[11px] font-bold text-[#60708d] dark:text-slate-400 mb-1.5 uppercase tracking-wider flex items-center gap-1.5">
            <Filter className="h-3 w-3" /> Filter by Letter (A - Z):
          </div>
          <div className="flex flex-wrap gap-1">
            {ALPHABETS.map((letter) => (
              <button
                key={letter}
                onClick={() => setSelectedLetter(letter)}
                className={`px-2.5 py-1 text-xs rounded-md font-bold transition ${
                  selectedLetter === letter
                    ? 'bg-brand text-white shadow-sm'
                    : 'bg-slate-50 text-slate-600 hover:bg-slate-100 dark:bg-[#11192e] dark:border dark:border-[#1e293b] dark:text-slate-300 dark:hover:bg-[#1a2542]'
                }`}
              >
                {letter}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Companies Results */}
      {loading ? (
        <LoadingState label="Loading all companies from PostgreSQL..." />
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-[#60708d] dark:text-slate-400 px-1">
            <span>
              Showing <b>{startItem}</b> to <b>{endItem}</b> of <b>{companies.length}</b> companies
            </span>
            <span>
              Page <b>{page}</b> of <b>{totalPages}</b>
            </span>
          </div>

          <div className="grid gap-3.5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {paginatedCompanies.map((company) => {
              const isTarget = target === company.company_id;
              return (
                <article
                  key={company.company_id}
                  className={`soft-card p-4 flex flex-col justify-between transition-all hover:shadow-md border ${
                    isTarget ? 'border-brand ring-2 ring-brand/10 dark:ring-brand/20' : 'border-line dark:border-[#1e293b]'
                  }`}
                >
                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between gap-2.5">
                      <div className="flex items-center gap-2.5 min-w-0">
                        <div className="grid h-10 w-10 place-items-center rounded-lg bg-[#eef2ff] dark:bg-[#18233f] font-bold text-brand dark:text-[#818cf8] text-xs shrink-0">
                          {company.logo || company.name.slice(0, 2).toUpperCase()}
                        </div>
                        <div className="min-w-0">
                          {/* Company Name clearly visible in dark and light modes */}
                          <h2 className="text-sm font-bold text-slate-800 dark:text-white truncate" title={company.name}>
                            {company.name}
                          </h2>
                          <span className="text-[11px] text-slate-400 dark:text-slate-400 font-medium">
                            {company.total_questions ? `${company.total_questions} OA Questions` : 'Curated Bank'}
                          </span>
                        </div>
                      </div>
                      {isTarget && (
                        <span className="shrink-0 p-1 bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 rounded-full" title="Current Primary Target">
                          <CheckCircle2 className="h-3.5 w-3.5" />
                        </span>
                      )}
                    </div>

                    <p className="line-clamp-2 text-xs text-[#60708d] dark:text-slate-400">
                      {company.description || `Company-specific OA and interview preparation profile for ${company.name}.`}
                    </p>
                  </div>

                  <div className="mt-3.5 pt-2.5 border-t border-line dark:border-[#1e293b] flex items-center gap-2">
                    <button
                      className={`text-xs flex-1 py-1.5 px-2.5 rounded-lg font-semibold transition ${
                        isTarget
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800'
                          : 'bg-slate-100 hover:bg-slate-200 text-slate-700 dark:bg-[#1e293b] dark:hover:bg-[#283852] dark:text-slate-200 dark:border dark:border-[#334155]'
                      }`}
                      onClick={() => selectTarget(company.company_id, company.name)}
                    >
                      {isTarget ? 'Targeted' : 'Set Target'}
                    </button>
                    <Link
                      className="primary-btn text-xs py-1.5 px-2.5 flex items-center gap-1 shrink-0"
                      to={`/companies/${company.company_id}`}
                    >
                      View <ArrowRight className="h-3 w-3" />
                    </Link>
                  </div>
                </article>
              );
            })}
          </div>

          {!companies.length && (
            <div className="soft-card p-8 text-center text-[#60708d] dark:text-slate-400 space-y-1.5">
              <p className="font-semibold text-sm text-ink dark:text-white">No companies found.</p>
              <p className="text-xs">Try selecting a different letter filter or clearing your search term.</p>
            </div>
          )}

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="card p-3.5 flex flex-col sm:flex-row items-center justify-between gap-3 dark:border-[#1e293b]">
              <div className="text-xs text-[#60708d] dark:text-slate-400">
                Showing <b>{startItem}</b> to <b>{endItem}</b> of <b>{companies.length}</b>
              </div>

              <div className="flex items-center gap-1.5">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="secondary-btn text-xs py-1 px-2.5 flex items-center gap-1 disabled:opacity-40 dark:border-[#1e293b] dark:bg-[#162038] dark:text-slate-200"
                >
                  <ArrowLeft className="h-3 w-3" /> Previous
                </button>

                <div className="flex items-center gap-1 text-xs">
                  {Array.from({ length: Math.min(6, totalPages) }, (_, i) => {
                    let pageNum = page;
                    if (page <= 3) {
                      pageNum = i + 1;
                    } else if (page >= totalPages - 3) {
                      pageNum = totalPages - 5 + i;
                    } else {
                      pageNum = page - 2 + i;
                    }
                    if (pageNum < 1 || pageNum > totalPages) return null;

                    return (
                      <button
                        key={pageNum}
                        onClick={() => setPage(pageNum)}
                        className={`w-7 h-7 rounded-md font-bold transition ${
                          page === pageNum
                            ? 'bg-brand text-white shadow-sm'
                            : 'bg-slate-50 hover:bg-slate-100 text-slate-700 dark:bg-[#11192e] dark:border dark:border-[#1e293b] dark:text-slate-300 dark:hover:bg-[#1e293b]'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>

                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  className="secondary-btn text-xs py-1 px-2.5 flex items-center gap-1 disabled:opacity-40 dark:border-[#1e293b] dark:bg-[#162038] dark:text-slate-200"
                >
                  Next <ArrowRight className="h-3 w-3" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
