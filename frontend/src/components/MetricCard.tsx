export function MetricCard({ label, value, note, icon }: { label: string; value: string; note: React.ReactNode; icon: React.ReactNode }) {
  return (
    <article className="soft-card p-4 sm:p-4.5">
      <div className="flex items-start justify-between">
        <p className="text-xs font-semibold text-[#405476] dark:text-slate-400">{label}</p>
        <div className="metric-icon">{icon}</div>
      </div>
      <div className="mt-3 text-2xl font-black text-ink dark:text-white">{value}</div>
      <div className="mt-1 text-xs text-[#8a9ab4] dark:text-slate-400">{note}</div>
    </article>
  );
}
