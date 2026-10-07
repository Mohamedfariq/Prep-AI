export function LoadingState({ label = 'Loading data...' }: { label?: string }) {
  return <div className="soft-card p-6 text-muted">{label}</div>;
}

export function EmptyState({ title, body, action }: { title: string; body: string; action?: React.ReactNode }) {
  return (
    <div className="soft-card p-8">
      <h3 className="text-xl font-bold">{title}</h3>
      <p className="mt-2 max-w-2xl text-muted">{body}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
