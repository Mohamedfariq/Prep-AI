import { useEffect, useState } from 'react';
import { Award, CheckCircle2, ChevronRight, HelpCircle, RefreshCw, Star } from 'lucide-react';
import { LoadingState } from '../components/State';
import { api } from '../services/api';

interface DiagnosticQuestion {
  id: string;
  topic_id: string;
  topic_name: string;
  question: string;
  options: string[];
}

export function SkillProfile() {
  const [skills, setSkills] = useState<any[]>([]);
  const [profileSummary, setProfileSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  // Diagnostic Quiz Modal State
  const [showDiagnostic, setShowDiagnostic] = useState(false);
  const [questions, setQuestions] = useState<DiagnosticQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [quizLoading, setQuizLoading] = useState(false);
  const [quizResult, setQuizResult] = useState<any>(null);

  function fetchSkills() {
    setLoading(true);
    api.get('/api/candidate/skill-profile')
      .then((res) => {
        setSkills(res.data.skills || []);
        setProfileSummary(res.data.profile || {});
      })
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    fetchSkills();
  }, []);

  async function openDiagnostic() {
    setShowDiagnostic(true);
    setQuizResult(null);
    setAnswers({});
    setQuizLoading(true);
    try {
      const res = await api.get('/api/candidate/diagnostic/questions');
      setQuestions(res.data || []);
    } catch (e) {
      console.error('Failed to load diagnostic questions', e);
    } finally {
      setQuizLoading(false);
    }
  }

  async function submitDiagnostic() {
    const formattedAnswers = Object.entries(answers).map(([question_id, selected_index]) => ({
      question_id,
      selected_index,
    }));

    setQuizLoading(true);
    try {
      const res = await api.post('/api/candidate/diagnostic/submit', { answers: formattedAnswers });
      setQuizResult(res.data);
      fetchSkills();
    } catch (e) {
      console.error('Failed to submit diagnostic', e);
    } finally {
      setQuizLoading(false);
    }
  }

  const categories = ['ALL', 'DSA', 'CS Fundamentals', 'Languages'];
  const filteredSkills = selectedCategory === 'ALL'
    ? skills
    : skills.filter((s) => s.category === selectedCategory);

  if (loading) return <LoadingState />;

  return (
    <div className="space-y-4 max-w-5xl pb-12">
      <section className="card p-5 sm:p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-ink dark:text-white">Skill Mastery Profile</h1>
          <p className="mt-1 text-xs sm:text-sm text-[#60708d] dark:text-slate-400">
            Bayesian Knowledge Tracing (BKT) topic mastery initialized by self-rating and 15-question diagnostic calibration.
          </p>
        </div>
        <button
          onClick={openDiagnostic}
          className="primary-btn text-xs py-2 px-3.5 flex items-center gap-2 whitespace-nowrap self-start md:self-auto"
        >
          <Award className="h-4 w-4" /> Take Diagnostic Quiz (15 Qs)
        </button>
      </section>

      {/* Summary KPI Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="soft-card p-4">
          <span className="text-[11px] font-semibold text-[#60708d] dark:text-slate-400 uppercase tracking-wider">Overall BKT Mastery</span>
          <div className="mt-1.5 text-2xl font-black text-brand dark:text-[#818cf8]">
            {Math.round((profileSummary?.overall_mastery || 0) * 100)}%
          </div>
        </div>
        <div className="soft-card p-4">
          <span className="text-[11px] font-semibold text-[#60708d] dark:text-slate-400 uppercase tracking-wider">Diagnostic Accuracy</span>
          <div className="mt-1.5 text-2xl font-black text-emerald-600 dark:text-emerald-400">
            {profileSummary?.accuracy ? `${profileSummary.accuracy}%` : 'Not Taken'}
          </div>
        </div>
        <div className="soft-card p-4">
          <span className="text-[11px] font-semibold text-[#60708d] dark:text-slate-400 uppercase tracking-wider">Target Company</span>
          <div className="mt-1.5 text-2xl font-black capitalize text-slate-800 dark:text-white">
            {profileSummary?.target_company || 'Unset'}
          </div>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex gap-1.5 border-b border-line dark:border-[#1e293b] pb-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              selectedCategory === cat
                ? 'bg-brand text-white shadow-sm'
                : 'text-[#60708d] dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-[#1e293b]'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Skill List */}
      <div className="soft-card p-5">
        <div className="space-y-4">
          {filteredSkills.map((skill) => {
            const mastery = Math.round((skill.mastery_probability || 0) * 100);
            return (
              <div key={skill.topic_id || skill.topic} className="space-y-1">
                <div className="flex justify-between items-center text-xs sm:text-sm">
                  <div>
                    <span className="font-bold text-[#0f172a] dark:text-white">{skill.topic}</span>
                    <span className="ml-2 text-[10px] px-2 py-0.5 rounded-full bg-slate-100 dark:bg-[#1e293b] text-slate-600 dark:text-slate-300">
                      {skill.category}
                    </span>
                  </div>
                  <div className="text-xs text-[#60708d] dark:text-slate-400">
                    <span className="font-semibold text-brand dark:text-[#818cf8]">{mastery}% Mastery</span>
                    <span className="mx-1.5">•</span>
                    <span>Self-Rate: {skill.self_rating || 2.5}/5</span>
                  </div>
                </div>
                <div className="h-2 rounded-full bg-[#eef2f7] dark:bg-[#1e293b] overflow-hidden">
                  <div
                    className="h-full rounded-full bg-brand dark:bg-[#6366f1] transition-all duration-500"
                    style={{ width: `${mastery}%` }}
                  />
                </div>
              </div>
            );
          })}
          {!filteredSkills.length && (
            <p className="text-muted dark:text-slate-400 text-center py-6 text-xs">No skills found in this category.</p>
          )}
        </div>
      </div>

      {/* Diagnostic Modal */}
      {showDiagnostic && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-white dark:bg-[#0e1424] dark:border dark:border-[#1e293b] rounded-2xl max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl">
            <div className="p-4 sm:p-5 border-b border-line dark:border-[#1e293b] flex justify-between items-center">
              <div>
                <h3 className="text-lg font-bold text-ink dark:text-white">15-Question Initial Diagnostic Assessment</h3>
                <p className="text-xs text-[#60708d] dark:text-slate-400 mt-0.5">
                  Calibrate your prior Bayesian mastery across DSA and CS fundamentals.
                </p>
              </div>
              <button
                onClick={() => setShowDiagnostic(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-white text-base font-bold p-1"
              >
                ✕
              </button>
            </div>

            <div className="p-4 sm:p-5 overflow-y-auto flex-1 space-y-4">
              {quizLoading ? (
                <div className="py-12 text-center text-[#60708d] dark:text-slate-400 text-xs">Loading questions...</div>
              ) : quizResult ? (
                <div className="space-y-3.5 text-center py-5">
                  <div className="w-14 h-14 bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 rounded-full flex items-center justify-center mx-auto">
                    <CheckCircle2 className="h-7 w-7" />
                  </div>
                  <h4 className="text-xl font-black text-ink dark:text-white">Assessment Complete!</h4>
                  <p className="text-slate-600 dark:text-slate-300 text-xs sm:text-sm">
                    Accuracy: <b>{quizResult.accuracy_percentage}%</b> ({quizResult.correct_count} / {quizResult.total_questions} correct)
                  </p>
                  <p className="text-xs text-[#60708d] dark:text-slate-400">
                    Your topic priors have been calibrated using the 70/30 diagnostic + self-rating formula.
                  </p>
                  <button
                    onClick={() => setShowDiagnostic(false)}
                    className="primary-btn mt-3 inline-block text-xs py-2 px-4"
                  >
                    Done & View Updated Profile
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {questions.map((q, qIndex) => (
                    <div key={q.id} className="p-3.5 rounded-xl border border-line dark:border-[#1e293b] bg-slate-50/50 dark:bg-[#11192e] space-y-2.5">
                      <div className="flex items-start justify-between gap-2">
                        <span className="font-bold text-xs sm:text-sm text-[#0f172a] dark:text-white">
                          {qIndex + 1}. {q.question}
                        </span>
                        <span className="text-[9px] font-semibold uppercase px-2 py-0.5 rounded bg-blue-100 text-blue-700 dark:bg-[#18233f] dark:text-[#818cf8] whitespace-nowrap">
                          {q.topic_name}
                        </span>
                      </div>
                      <div className="space-y-1.5">
                        {q.options.map((opt, optIndex) => (
                          <label
                            key={optIndex}
                            className={`flex items-center gap-2.5 p-2.5 rounded-lg border text-xs cursor-pointer transition ${
                              answers[q.id] === optIndex
                                ? 'border-brand bg-brand/5 dark:bg-brand/15 text-brand dark:text-[#818cf8] font-semibold'
                                : 'border-line dark:border-[#1e293b] bg-white dark:bg-[#162038] hover:bg-slate-50 dark:hover:bg-[#1c2844] text-slate-700 dark:text-slate-200'
                            }`}
                          >
                            <input
                              type="radio"
                              name={q.id}
                              checked={answers[q.id] === optIndex}
                              onChange={() => setAnswers({ ...answers, [q.id]: optIndex })}
                              className="accent-brand"
                            />
                            <span>{opt}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {!quizResult && !quizLoading && (
              <div className="p-3 sm:p-4 border-t border-line dark:border-[#1e293b] bg-slate-50 dark:bg-[#0b101f] flex justify-between items-center">
                <span className="text-xs text-[#60708d] dark:text-slate-400">
                  Answered: {Object.keys(answers).length} of {questions.length}
                </span>
                <button
                  onClick={submitDiagnostic}
                  disabled={Object.keys(answers).length === 0}
                  className="primary-btn text-xs py-1.5 px-3.5"
                >
                  Submit & Calibrate Mastery
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

