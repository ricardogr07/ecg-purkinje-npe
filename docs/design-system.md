# Design system, conduction-lens demo (dark mode)

Dark, clean, developer aesthetic. Inspiration: ricardogr07.github.io and shelter-pulse.com (near-black surfaces, flat cards, one blue accent, monospace for data, subtle borders, no gradients or heavy shadows). This documents the tokens, components, and patterns the `ui/` build should use, and how to connect Figma.

## Design tokens

### Color (dark)
| Token | Value | Use |
|---|---|---|
| `--bg-900` | #0a0b0d | page background (near-black) |
| `--bg-800` | #111318 | section surface |
| `--bg-700` | #1a1d23 | card / elevated |
| `--bg-hover` | #22262e | hover surface |
| `--border` | #23272f | default border (1px) |
| `--border-strong` | #333a45 | emphasized border |
| `--text` | #e6e8ec | primary text |
| `--text-dim` | #9aa1ad | secondary text |
| `--text-faint` | #6b7280 | captions, meta |
| `--accent` | #4f8cff | brand blue, links, active |
| `--accent-dim` | #22406e | accent hover / subtle accent bg |
| `--pinned` | #34d399 | identifiable (green) |
| `--partial` | #fbbf24 | partially identifiable (amber) |
| `--unknown` | #6b7280 | unidentified (grey) |
| `--danger` | #f87171 | fail / before-calibration |
| `--ok` | #34d399 | pass / after-calibration |
| `--warn-bg` | #2a2213 | honesty-badge background |

Two meaning ramps only: the identifiability ramp (`--pinned`/`--partial`/`--unknown`) and status (`--ok`/`--danger`). Everything else is neutral. Any color that encodes meaning gets a 1-line legend.

### Typography
- Sans: Inter, system-ui, sans-serif. Mono: "JetBrains Mono", ui-monospace, monospace (parameter names, numbers).
- Scale: display 34/1.12/750; h1 28/1.2/700; h2 20/1.3/650; h3 16/1.4/600; body 15/1.55/400; small 13; data-mono 13.

### Spacing / radius / motion
- Spacing scale (px): 4, 8, 12, 16, 24, 32, 48, 64.
- Radius: sm 8, md 12, lg 16, pill 999. Border width 1px.
- Elevation: flat. Depth comes from surface lightening (`--bg-800` -> `--bg-700`) + 1px border, not shadows. Optional 1px accent ring on focus.
- Motion: 150ms ease-out for hover/focus; 300ms ease for scroll reveals; respect `prefers-reduced-motion`.

## Components
| Component | Variants | States | Notes |
|---|---|---|---|
| Button | primary (accent), secondary (bordered), ghost | default, hover, active, disabled, loading | 36px md; focus ring `--accent` |
| Card | default, elevated | default, hover | `--bg-700`, 1px `--border`, radius lg |
| Chip / Badge | default, warn (honesty), success, danger | static | pill; warn = `--warn-bg` + amber text |
| StatChip | default | static | big number + caption; hero stats |
| NavPill | default, active | hover | header nav; active = accent text |
| SpectrumBar | pinned, partial, unknown | static | horizontal bar, width = contraction; color by ramp |
| CalibrationBadge | before (danger), after (ok) | static | SBC pass/fail |
| PipelineNode | default, hot (accent) | static | theta -> tree -> ECG -> NPE -> posterior |
| HeartViewer3D | crtdemo, strocchi | idle, rotating, loading | react-three-fiber canvas; activation colormap; orbit controls |
| Section | default | reveal-on-scroll | max-width 960px, generous vertical rhythm |
| Footer | default | static | Built with Claude + links |

Accessibility: every interactive element keyboard-reachable with a visible `--accent` focus ring; the 3D canvas has a text alt describing what it shows; charts have an sr-only summary; color is never the only signal (bars carry a text verdict too).

## Patterns
- **Hero:** eyebrow + question headline + two-part-finding sub + 3 StatChips (one is the synthetic-truth honesty chip).
- **Identifiability spectrum:** SpectrumBars, low-to-high contraction, legend. The money shot.
- **Calibration before/after:** two CalibrationBadges with an arrow; TARP line below.
- **Pipeline strip:** 5 PipelineNodes.
- **3D heart viewer:** HeartViewer3D with a param/lead caption; crtdemo and (when ready) Strocchi.
- **Fidelity panel:** two bars (0.20 -> 0.79) with the "diagnosed, not hidden" caption.

## How to connect Figma (for schema generation)
There is no standalone "Claude Design" app; design work runs through the design-plugin skills plus the Figma connector (MCP). The connector needs an interactive OAuth that a non-interactive Cowork session cannot perform. To enable it:
1. In an interactive Claude session (claude.ai or the desktop app), open connector settings and connect Figma, or run `/mcp` in Claude Code and authorize the Figma server. Approve the OAuth in the browser.
2. Once authorized, the Figma MCP tools (get_design_context, get_screenshot, create_new_file, use_figma) and the design skills become usable in that session.
3. Then invoke the design skills against this doc: `design-system` (tokens), `ux-copy` (section copy), `design-handoff` (spec sheet), and push a starter file with `use_figma` / `create_new_file` using the tokens above.
4. Alternatively (no Figma): Claude Code builds `ui/` directly from these tokens plus the rendered mockup; Figma is optional polish, not on the critical path.
