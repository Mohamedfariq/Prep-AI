import { useEffect, useState } from 'react';
import { LoadingState } from '../components/State';
import { api } from '../services/api';
import type { SkillRow } from '../types/api';

export function SkillProfile() {
  const [skills, setSkills] = useState<SkillRow[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.get('/api/candidate/skill-profile').then((response) => setSkills(response.data.skills || [])).finally(() => setLoading(false));
  }, []);
  if (loading) return <LoadingState />;
  return (
    <div className="space-y-6">
      <section className="card p-8"><h1 className="text-3xl font-extrabold">Skill Profile</h1><p className="mt-2 text-[#60708d]">BKT topic mastery, accuracy, attempts, and progress indicators.</p></section>
      <div className="soft-card p-6">
        <div className="space-y-5">
          {skills.map((skill) => {
            const value = Math.round(skill.mastery_probability * 100);
            return (
              <div key={skill.topic}>
                <div className="mb-2 flex justify-between"><b>{skill.topic}</b><span>{value}% • {skill.attempts} attempts</span></div>
                <div className="h-3 rounded-full bg-[#eef2f7]"><div className="h-full rounded-full bg-brand" style={{ width: `${value}%` }} /></div>
              </div>
            );
          })}
          {!skills.length && <p className="text-muted">No mastery profile yet. Complete a diagnostic assessment first.</p>}
        </div>
      </div>
    </div>
  );
}
