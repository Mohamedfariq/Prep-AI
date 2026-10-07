import { Bot, Braces, Code2, Network } from 'lucide-react';

const tracks = [
  { title: 'Data Structures', icon: Braces, copy: 'Arrays, trees, graphs, heaps, strings, and hash-based design.' },
  { title: 'Algorithms', icon: Network, copy: 'Greedy, dynamic programming, traversal, sorting, and search strategies.' },
  { title: 'Coding Interview', icon: Code2, copy: 'Problem decomposition, edge cases, complexity, and communication.' },
  { title: 'System Design', icon: Bot, copy: 'Extensible architecture placeholder for future interview modules.' },
];

export function Interview() {
  return (
    <div className="space-y-6">
      <section className="card p-8">
        <h1 className="text-3xl font-extrabold">Interview Preparation</h1>
        <p className="mt-2 max-w-3xl text-[#60708d]">Adaptive technical interview preparation based on the candidate skill profile. LLM interviewer integration is intentionally left as a future extension.</p>
      </section>
      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {tracks.map((track) => <article className="soft-card p-6" key={track.title}><track.icon className="text-brand" /><h2 className="mt-4 text-xl font-bold">{track.title}</h2><p className="mt-2 text-[#60708d]">{track.copy}</p></article>)}
      </section>
    </div>
  );
}
