import { ExternalLink, Search } from 'lucide-react';
import { useEffect, useState } from 'react';
import { LoadingState } from '../components/State';
import { api } from '../services/api';
import type { Question } from '../types/api';

export function QuestionBank() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [search, setSearch] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handle = setTimeout(() => {
      api.get('/api/questions', { params: { search: search || undefined, difficulty: difficulty || undefined } })
        .then((response) => setQuestions(response.data.items || []))
        .finally(() => setLoading(false));
    }, 250);
    return () => clearTimeout(handle);
  }, [search, difficulty]);

  return (
    <div className="space-y-6">
      <section className="card p-8">
        <h1 className="text-3xl font-extrabold">Question Bank</h1>
        <p className="mt-2 text-[#60708d]">Search and filter company-specific coding questions.</p>
        <div className="mt-6 grid gap-4 md:grid-cols-[1fr_220px]">
          <div className="input-shell bg-white ring-1 ring-line"><Search className="h-5 w-5" /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search questions..." /></div>
          <select className="input-shell bg-white ring-1 ring-line" value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
            <option value="">All Difficulties</option><option>Easy</option><option>Medium</option><option>Hard</option>
          </select>
        </div>
      </section>
      {loading ? <LoadingState /> : (
        <div className="soft-card overflow-hidden">
          <table className="w-full min-w-[900px] text-left">
            <thead className="bg-[#f4f7fb] text-sm text-[#60708d]"><tr><th className="p-4">Question</th><th>Topics</th><th>Difficulty</th><th>Frequency</th><th>Status</th><th /></tr></thead>
            <tbody>
              {questions.map((q) => (
                <tr className="border-t border-line" key={q.question_id}>
                  <td className="p-4 font-semibold">{q.title}</td>
                  <td className="text-sm text-[#60708d]">{q.topics?.slice(0, 3).join(', ')}</td>
                  <td><span className="rounded-lg bg-[#eef2ff] px-2 py-1 text-sm">{q.difficulty}</span></td>
                  <td>{q.frequency_percent}%</td>
                  <td>{q.status}</td>
                  <td><a href={q.leetcode_url} target="_blank" rel="noreferrer"><ExternalLink className="h-5 w-5" /></a></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
