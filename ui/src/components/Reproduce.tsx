// Reproduce it. Four cards: the ledger, the weights + container, and the two
// licenses. Copy and links verbatim from the frozen standalone.

const CARDS = [
  {
    title: "The paper",
    hint: "IEEE / Zenodo manuscript",
    body: "The full write-up: methods, the calibrated identifiability spectrum, calibration, and the honest limitations, as a self-contained IEEE-format paper.",
    href: "https://github.com/ricardogr07/ecg-purkinje-npe/blob/main/technical-writeup/ieee-paper/paper.pdf",
    linkText: "Read the paper (PDF)",
  },
  {
    title: "Verification ledger",
    hint: "every claim, checked",
    body: "The record of what was claimed, what was checked, and what was retracted. The corrections above are drawn from it.",
    href: "https://github.com/ricardogr07/ecg-purkinje-npe/blob/main/docs/verification-ledger.md",
    linkText: "docs/verification-ledger.md",
  },
  {
    title: "Weights and container",
    hint: "the trained network and its environment",
    body: "The trained posterior estimator and a container image that pins the full environment, so a run reproduces bit for bit.",
    href: "https://github.com/ricardogr07/ecg-purkinje-npe",
    linkText: "github.com/ricardogr07/ecg-purkinje-npe",
  },
  {
    title: "Code license",
    hint: "Apache-2.0",
    body: "All code in this project is released under Apache-2.0. Use it, fork it, build on it.",
  },
  {
    title: "Data license",
    hint: "Strocchi CC-BY-4.0",
    body: "The Strocchi biventricular mesh cohort is used under CC-BY-4.0, with attribution to the original authors.",
  },
];

export default function Reproduce() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {CARDS.map((c) => (
        <div key={c.title} className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-5">
          <div className="flex items-baseline justify-between gap-3">
            <h3 className="text-sm font-semibold text-zinc-100">{c.title}</h3>
            <span className="text-xs text-zinc-500">{c.hint}</span>
          </div>
          <p className="mt-3 text-sm leading-relaxed text-zinc-400">{c.body}</p>
          {c.href ? (
            <a
              href={c.href}
              className="mt-3 inline-block font-mono text-xs text-indigo-300 underline underline-offset-2 hover:text-indigo-200 wrap-break-word"
            >
              {c.linkText}
            </a>
          ) : null}
        </div>
      ))}
    </div>
  );
}
