// Static footer. Credits + license line
// (github / personal site / linkedin, with icons). Copy and links verbatim from
// the frozen standalone. Not a page-level banner: it makes no data claim.

const LINKS = [
  {
    label: "GitHub",
    href: "https://github.com/ricardogr07",
    icon: (
      <path d="M12 2C6.48 2 2 6.58 2 12.25c0 4.53 2.87 8.37 6.84 9.73.5.1.68-.22.68-.49 0-.24-.01-.87-.01-1.71-2.78.62-3.37-1.37-3.37-1.37-.45-1.18-1.11-1.49-1.11-1.49-.91-.64.07-.62.07-.62 1 .07 1.53 1.05 1.53 1.05.89 1.56 2.34 1.11 2.91.85.09-.66.35-1.11.63-1.37-2.22-.26-4.56-1.14-4.56-5.06 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.3.1-2.7 0 0 .84-.28 2.75 1.05a9.36 9.36 0 0 1 5 0c1.91-1.33 2.75-1.05 2.75-1.05.55 1.4.2 2.44.1 2.7.64.72 1.03 1.63 1.03 2.75 0 3.93-2.34 4.79-4.57 5.05.36.32.68.94.68 1.9 0 1.37-.01 2.48-.01 2.82 0 .27.18.6.69.49A10.02 10.02 0 0 0 22 12.25C22 6.58 17.52 2 12 2Z" />
    ),
  },
  {
    label: "Personal site",
    href: "https://ricardogr07.github.io/",
    icon: (
      <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm6.93 6h-2.95a15.7 15.7 0 0 0-1.38-3.56A8.03 8.03 0 0 1 18.93 8ZM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 1.08-2.76 1.91-3.96ZM4.26 14a7.96 7.96 0 0 1 0-4h3.38a16.5 16.5 0 0 0 0 4H4.26Zm.81 2h2.95c.35 1.28.82 2.49 1.38 3.56A8.03 8.03 0 0 1 5.07 16Zm2.95-8H5.07a8.03 8.03 0 0 1 4.33-3.56A15.7 15.7 0 0 0 8.02 8ZM12 19.96c-.83-1.2-1.48-2.53-1.91-3.96h3.82c-.43 1.43-1.08 2.76-1.91 3.96ZM14.34 14H9.66a14.7 14.7 0 0 1 0-4h4.68a14.7 14.7 0 0 1 0 4Zm.28 5.56c.56-1.07 1.03-2.28 1.38-3.56h2.95a8.03 8.03 0 0 1-4.33 3.56ZM16.36 14a16.5 16.5 0 0 0 0-4h3.38a7.96 7.96 0 0 1 0 4h-3.38Z" />
    ),
  },
  {
    label: "LinkedIn",
    href: "https://www.linkedin.com/in/ricardogarciaramirez/",
    icon: (
      <path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5ZM3 9h4v12H3V9Zm7 0h3.83v1.64h.05c.53-1 1.83-2.06 3.77-2.06 4.03 0 4.77 2.65 4.77 6.1V21h-4v-5.4c0-1.29-.02-2.95-1.8-2.95-1.8 0-2.08 1.4-2.08 2.85V21h-4V9Z" />
    ),
  },
];

export default function Footer() {
  return (
    <footer className="border-t border-zinc-800 py-12">
      <div className="mx-auto max-w-6xl px-4 text-center">
        <p className="text-sm text-zinc-300">
          <span className="font-semibold text-zinc-100">Conduction Lens</span> · Calibrated
          identifiability of the conduction system from the surface ECG
        </p>
        <p className="mt-3 text-sm text-zinc-400">
          Built for{" "}
          <a
            href="https://cerebralvalley.ai/e/built-with-claude-life-sciences"
            className="text-indigo-300 underline underline-offset-2 hover:text-indigo-200"
          >
            Built with Claude: Life Sciences
          </a>
        </p>
        <p className="mt-1 text-sm text-zinc-400">Built by Ricardo García Ramírez</p>

        <div className="mt-4 flex items-center justify-center gap-4">
          {LINKS.map((l) => (
            <a
              key={l.label}
              href={l.href}
              aria-label={l.label}
              className="text-zinc-500 hover:text-zinc-200"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5" aria-hidden="true">
                {l.icon}
              </svg>
            </a>
          ))}
        </div>

        <p className="mt-8 text-xs text-zinc-500">
          Code Apache-2.0 · Strocchi mesh cohort CC-BY-4.0 · Synthetic-truth study, no patient data
        </p>
      </div>
    </footer>
  );
}
