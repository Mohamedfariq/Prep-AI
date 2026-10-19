import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

interface ThemeToggleProps {
  className?: string;
  showLabel?: boolean;
}

export function ThemeToggle({ className = '', showLabel = false }: ThemeToggleProps) {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      className={`group relative flex items-center gap-2 rounded-xl border p-2.5 transition-all duration-300 active:scale-95 ${
        isDark
          ? 'border-[#222f49] bg-[#11192e] text-amber-300 shadow-[0_0_18px_rgba(251,191,36,0.18)] hover:border-amber-400/40 hover:bg-[#16213c]'
          : 'border-[#cbd5e1] bg-white text-slate-700 shadow-sm hover:border-brand hover:bg-[#f5f8ff] hover:text-brand'
      } ${className}`}
    >
      <div className="relative flex h-5 w-5 items-center justify-center">
        {isDark ? (
          <Moon className="h-5 w-5 fill-amber-300 text-amber-300 transition-transform duration-500 ease-out group-hover:-rotate-12 group-hover:scale-110" />
        ) : (
          <Moon className="h-5 w-5 text-slate-600 transition-transform duration-500 ease-out group-hover:rotate-12 group-hover:scale-110 group-hover:text-brand" />
        )}
      </div>

      {showLabel && (
        <span className="text-xs font-semibold tracking-wide">
          {isDark ? 'Dark Mode' : 'Light Mode'}
        </span>
      )}
    </button>
  );
}
