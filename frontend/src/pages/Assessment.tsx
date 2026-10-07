import { Send } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { LoadingState } from '../components/State';
import { api } from '../services/api';
import type { Question } from '../types/api';

export function Assessment() {
  const { assessmentId } = useParams();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitted, setSubmitted] = useState<any>(null);
  useEffect(() => {
    api.get(`/api/assessments/${assessmentId}`).then((response) => setQuestions(response.data.questions || [])).finally(() => setLoading(false));
  }, [assessmentId]);
  async function submit() {
    const answers = questions.map((q, index) => ({ question_id: q.question_id, correct: index % 2 === 0 }));
    const response = await api.post(`/api/assessments/${assessmentId}/submit`, { answers });
    setSubmitted(response.data);
  }
  if (loading) return <LoadingState />;
  return (
    <div className="space-y-6">
      <section className="card p-8"><h1 className="text-3xl font-extrabold">Assessment Session</h1><p className="mt-2 text-[#60708d]">Timer, navigation, code editor, submit, and test-case panel.</p></section>
      <div className="grid gap-5 xl:grid-cols-[1fr_420px]">
        <div className="soft-card p-6">
          {questions.map((q, index) => <div className="border-b border-line py-4" key={q.question_id}><b>{index + 1}. {q.title}</b><p className="text-[#60708d]">{q.topics?.join(', ')} • {q.difficulty}</p></div>)}
        </div>
        <div className="soft-card p-6">
          <h2 className="text-xl font-bold">Code Editor</h2>
          <textarea className="mt-4 h-72 w-full rounded-xl border border-line bg-[#0f172a] p-4 font-mono text-sm text-white outline-none" defaultValue={'def solve():\n    pass'} />
          <button className="primary-btn mt-4 w-full" onClick={submit}><Send className="h-4 w-4" /> Submit Assessment</button>
          {submitted && <div className="mt-4 rounded-xl bg-emerald-50 p-4 text-emerald-700">Score: {submitted.score} • Accuracy: {submitted.accuracy}%</div>}
        </div>
      </div>
    </div>
  );
}
