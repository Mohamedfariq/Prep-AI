export function LoadingState({ label = 'Loading data...' }: { label?: string }) {
  return <div className="soft-card p-4 text-xs sm:text-sm text-muted dark:text-slate-400">{label}</div>;
}

export function EmptyState({ title, body, action }: { title: string; body: string; action?: React.ReactNode }) {
  return (
    <div className="soft-card p-5 sm:p-6">
      <h3 className="text-lg font-bold text-ink dark:text-white">{title}</h3>
      <p className="mt-1.5 max-w-2xl text-xs sm:text-sm text-muted dark:text-slate-400">{body}</p>
      {action && <div className="mt-3.5">{action}</div>}
    </div>
  );
}
