// Shared layout primitives (section shell, card, chip, empty state). Mirrors the
// zinc/backdrop idiom.
import type { ReactNode } from "react";

export function Section({
  id,
  number,
  eyebrow,
  title,
  lead,
  children,
}: {
  id?: string;
  number?: string;
  eyebrow?: string;
  title: string;
  lead?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section id={id} className="border-t border-zinc-800/80 py-16 sm:py-24 scroll-mt-20">
      <div className="max-w-6xl mx-auto px-4">
        <div>
          {eyebrow ? (
            <p className="text-xs font-mono uppercase tracking-widest text-indigo-400 mb-3">
              {number ? <span className="text-zinc-500">{number} / </span> : null}
              {eyebrow}
            </p>
          ) : null}
          <h2 className="font-serif text-2xl sm:text-3xl font-semibold text-zinc-50 tracking-tight">
            {title}
          </h2>
          {lead ? <p className="mt-4 text-lg text-zinc-400 leading-relaxed">{lead}</p> : null}
        </div>
        <div className="mt-8">{children}</div>
      </div>
    </section>
  );
}

export function Card({
  children,
  className = "",
  title,
  hint,
}: {
  children: ReactNode;
  className?: string;
  title?: string;
  hint?: string;
}) {
  return (
    <div
      className={`rounded-2xl border border-zinc-800 bg-zinc-900/50 backdrop-blur p-4 sm:p-5 ${className}`}
    >
      {title ? (
        <div className="flex items-baseline justify-between gap-3 mb-3">
          <h3 className="text-sm font-semibold text-zinc-200">{title}</h3>
          {hint ? <span className="text-xs text-zinc-500">{hint}</span> : null}
        </div>
      ) : null}
      {children}
    </div>
  );
}

export function Chip({ children, tone = "zinc" }: { children: ReactNode; tone?: string }) {
  const tones: Record<string, string> = {
    zinc: "border-zinc-700 text-zinc-300",
    indigo: "border-indigo-500/50 text-indigo-300 bg-indigo-500/10",
    emerald: "border-emerald-500/50 text-emerald-300 bg-emerald-500/10",
    amber: "border-amber-500/50 text-amber-300 bg-amber-500/10",
    rose: "border-rose-500/50 text-rose-300 bg-rose-500/10",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-mono ${tones[tone] ?? tones.zinc}`}
    >
      {children}
    </span>
  );
}

// Graceful-degradation placeholder for a missing optional artifact block.
export function EmptyState({ label }: { label: string }) {
  return (
    <div className="flex items-center justify-center rounded-xl border border-dashed border-zinc-800 bg-zinc-900/30 p-8 text-center text-sm text-zinc-500">
      {label}
    </div>
  );
}
