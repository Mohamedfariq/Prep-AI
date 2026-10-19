import { ArrowLeft, ArrowRight, ExternalLink, Filter, Search, SlidersHorizontal } from 'lucide-react';
import { useEffect, useState } from 'react';
import { LoadingState } from '../components/State';
import { api } from '../services/api';
import type { Question } from '../types/api';

const ALPHABETS = ['ALL', '#', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];

export function QuestionBank() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [search, setSearch] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [selectedLetter, setSelectedLetter] = useState('ALL');
  const [sortBy, setSortBy] = useState('title');
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(50);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  // Reset to page 1 whenever search, difficulty, letter or sortBy changes
  useEffect(() => {
    setPage(1);
  }, [search, difficulty, selectedLetter, sortBy]);

  useEffect(() => {
    setLoading(true);
    const handle = setTimeout(() => {
      api.get('/api/questions', {
        params: {
          search: search || undefined,
          difficulty: difficulty || undefined,
          letter: selectedLetter !== 'ALL' ? selectedLetter : undefined,
          sort_by: sortBy,
          page,
          limit,
        },
      })
        .then((response) => {
          setQuestions(response.data.items || []);
          setTotal(response.data.total || 0);
        })
        .catch((err) => console.error('Failed to load questions', err))
        .finally(() => setLoading(false));
    }, 200);

    return () => clearTimeout(handle);
  }, [search, difficulty, selectedLetter, sortBy, page, limit]);

  const totalPages = Math.ceil(total / limit) || 1;
  const startItem = total === 0 ? 0 : (page - 1) * limit + 1;
  const endItem = Math.min(page * limit, total);

  return (
    <div className="space-y-4 max-w-7xl pb-16">
      <section className="card p-5 sm:p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-extrabold text-ink dark:text-white">Question Bank</h1>
            <p className="mt-1 text-xs sm:text-sm text-[#60708d] dark:text-slate-400">
              Explore and practice across all <b>{total.toLocaleString()}</b> company-specific interview coding questions.
            </p>
          </div>
          <div className="flex items-center gap-2 self-start md:self-auto">
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-brand/10 text-brand dark:bg-brand/20 dark:text-[#818cf8]">
              {total.toLocaleString()} Problems Indexed
            </span>
          </div>
        </div>

        {/* Filter Controls Row */}
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_160px_180px_120px]">
          <div className="input-shell dark:bg-[#0b101f] dark:ring-1 dark:ring-[#1e293b]">
            <Search className="h-4 w-4 text-muted dark:text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search questions by title or keyword..."
            />
          </div>

          <select
            className="input-shell dark:bg-[#0b101f] dark:ring-1 dark:ring-[#1e293b] dark:text-slate-200 cursor-pointer"
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
          >
            <option value="" className="dark:bg-[#0b101f] dark:text-white">All Difficulties</option>
            <option value="Easy" className="dark:bg-[#0b101f] dark:text-white">Easy</option>
            <option value="Medium" className="dark:bg-[#0b101f] dark:text-white">Medium</option>
            <option value="Hard" className="dark:bg-[#0b101f] dark:text-white">Hard</option>
          </select>

          <select
            className="input-shell dark:bg-[#0b101f] dark:ring-1 dark:ring-[#1e293b] dark:text-slate-200 cursor-pointer"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="title" className="dark:bg-[#0b101f] dark:text-white">Alphabetical (A - Z)</option>
            <option value="frequency" className="dark:bg-[#0b101f] dark:text-white">Most Frequent in OAs</option>
            <option value="difficulty" className="dark:bg-[#0b101f] dark:text-white">By Difficulty</option>
          </select>

          <select
            className="input-shell dark:bg-[#0b101f] dark:ring-1 dark:ring-[#1e293b] dark:text-slate-200 cursor-pointer"
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
          >
            <option value={25} className="dark:bg-[#0b101f] dark:text-white">25 / page</option>
            <option value={50} className="dark:bg-[#0b101f] dark:text-white">50 / page</option>
            <option value={100} className="dark:bg-[#0b101f] dark:text-white">100 / page</option>
          </select>
        </div>

        {/* A-Z Alphabet Quick Bar */}
        <div className="mt-4 pt-3 border-t border-line dark:border-[#1e293b]">
          <div className="text-[11px] font-bold text-[#60708d] dark:text-slate-400 mb-1.5 uppercase tracking-wider flex items-center gap-1.5">
            <Filter className="h-3 w-3" /> Jump to Letter:
          </div>
          <div className="flex flex-wrap gap-1">
            {ALPHABETS.map((letter) => (
              <button
                key={letter}
                onClick={() => setSelectedLetter(letter)}
                className={`px-2 py-0.5 text-xs rounded-md font-bold transition ${
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

      {/* Questions Table */}
      {loading ? (
        <LoadingState label="Loading questions from PostgreSQL..." />
      ) : (
        <div className="soft-card overflow-hidden dark:border-[#1e293b]">
          <div className="px-5 py-3 border-b border-line dark:border-[#1e293b] flex items-center justify-between text-xs text-[#60708d] dark:text-slate-400 bg-white dark:bg-[#0d1424]">
            <span>
              Showing <b>{startItem}</b> to <b>{endItem}</b> of <b>{total.toLocaleString()}</b> questions
            </span>
            <span>
              Page <b>{page}</b> of <b>{totalPages}</b>
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[850px] text-left">
              <thead className="bg-[#f4f7fb] dark:bg-[#0f172a] text-[11px] font-bold uppercase tracking-wider text-[#60708d] dark:text-slate-400 border-b border-line dark:border-[#1e293b]">
                <tr>
                  <th className="p-3 w-12">#</th>
                  <th className="p-3">Question Title</th>
                  <th className="p-3">Topics</th>
                  <th className="p-3">Difficulty</th>
                  <th className="p-3">OA Frequency</th>
                  <th className="p-3">Companies</th>
                  <th className="p-3 text-center">Solve</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line dark:divide-[#1e293b] text-xs sm:text-sm">
                {questions.map((q, idx) => {
                  const diffColor =
                    q.difficulty === 'Easy'
                      ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:border-emerald-800 dark:text-emerald-300'
                      : q.difficulty === 'Medium'
                      ? 'border-amber-200 bg-amber-50 text-amber-700 dark:bg-amber-950/50 dark:border-amber-800 dark:text-amber-300'
                      : 'border-rose-200 bg-rose-50 text-rose-700 dark:bg-rose-950/50 dark:border-rose-800 dark:text-rose-300';

                  return (
                    <tr className="hover:bg-slate-50/70 dark:hover:bg-[#141e34] transition" key={q.question_id || q.id}>
                      <td className="p-3 text-xs text-slate-400 font-mono">
                        {startItem + idx}
                      </td>
                      <td className="p-3 font-semibold text-slate-800 dark:text-slate-100">
                        {q.title}
                      </td>
                      <td className="p-3 text-xs text-[#60708d] dark:text-slate-400 max-w-xs">
                        <div className="flex flex-wrap gap-1">
                          {q.topics?.slice(0, 3).map((t) => (
                            <span key={t} className="px-2 py-0.5 rounded bg-slate-100 dark:bg-[#1e293b] text-slate-600 dark:text-slate-300 text-[11px]">
                              {t}
                            </span>
                          ))}
                          {(q.topics?.length || 0) > 3 && (
                            <span className="text-slate-400">+{q.topics!.length - 3}</span>
                          )}
                        </div>
                      </td>
                      <td className="p-3">
                        <span className={`inline-block px-2.5 py-0.5 text-[11px] rounded-full border font-semibold ${diffColor}`}>
                          {q.difficulty}
                        </span>
                      </td>
                      <td className="p-3 text-slate-700 dark:text-slate-300 font-medium text-xs">
                        {q.frequency_percent ? `${Math.round(q.frequency_percent)}%` : '—'}
                      </td>
                      <td className="p-3 text-xs text-[#60708d] dark:text-slate-400">
                        <span className="capitalize">
                          {q.companies?.slice(0, 3).join(', ')}
                          {(q.companies?.length || 0) > 3 ? ` +${q.companies!.length - 3}` : ''}
                        </span>
                      </td>
                      <td className="p-3 text-center">
                        {q.leetcode_url ? (
                          <a
                            href={q.leetcode_url}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex p-1.5 text-brand dark:text-[#818cf8] hover:bg-brand/10 rounded-lg transition"
                            title="Open problem on LeetCode"
                          >
                            <ExternalLink className="h-3.5 w-3.5" />
                          </a>
                        ) : (
                          <span className="text-slate-300 dark:text-slate-600">—</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {!questions.length && (
            <div className="py-12 text-center text-[#60708d] dark:text-slate-400 space-y-1.5">
              <p className="font-semibold text-sm text-ink dark:text-white">No questions match your filter.</p>
              <p className="text-xs">Try selecting a different letter or clearing your search query.</p>
            </div>
          )}

          {/* Pagination Footer */}
          <div className="p-3 border-t border-line dark:border-[#1e293b] bg-white dark:bg-[#0d1424] flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="text-xs text-[#60708d] dark:text-slate-400">
              Showing <b>{startItem}</b> to <b>{endItem}</b> of <b>{total.toLocaleString()}</b>
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
                {/* Page Number Chips */}
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum = page;
                  if (page <= 3) {
                    pageNum = i + 1;
                  } else if (page >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
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
        </div>
      )}
    </div>
  );
}
