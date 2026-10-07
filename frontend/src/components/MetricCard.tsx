export function MetricCard({ label, value, note, icon }: { label: string; value: string; note: React.ReactNode; icon: React.ReactNode }) {
  return (
    <article className="soft-card p-6">
      <div className="flex items-start justify-between">
        <p className="font-medium text-[#405476]">{label}</p>
        <div className="metric-icon">{icon}</div>
      </div>
      <div className="mt-6 text-3xl font-extrabold">{value}</div>
      <div className="mt-1 text-[#8a9ab4]">{note}</div>
    </article>
  );
}
