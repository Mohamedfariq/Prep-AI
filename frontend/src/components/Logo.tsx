import { Zap } from 'lucide-react';

export function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand text-white shadow-subtle dark:shadow-[0_0_20px_rgba(99,102,241,0.35)]">
        <Zap className="h-7 w-7 fill-white" />
      </div>
      {!compact && (
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xl font-extrabold tracking-tight text-ink dark:text-white">PrepAI</span>
            <span className="rounded-lg bg-[#ece9ff] px-2 py-0.5 text-xs font-semibold text-[#2514a8] dark:bg-[#201c59] dark:text-[#a5b4fc]">
              OA PRO
            </span>
          </div>
          <p className="text-sm text-[#8a9ab4] dark:text-[#64748b]">Placement Intelligence</p>
        </div>
      )}
    </div>
  );
}

