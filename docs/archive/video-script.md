# Demo video script (~3 min, the scored submission artifact)

Tone: clear, confident, honest. The emotional core is the two-part thesis and the refused metric. ~450 words of narration (about 150 wpm). Each beat lists the on-screen VISUAL and the NARRATION. Human records the voiceover and uploads to YouTube.

---

**1. Hook (0:00 to 0:15)**
VISUAL: a 12-lead ECG scrolling, then it dissolves into the 3D heart with the activation wavefront lighting up (blue to red).
NARRATION: "Every heartbeat is timed by hidden electrical wiring inside your heart, the Purkinje network. When it fails, you get bundle branch block, and it is what pacemakers and CRT devices try to fix. The only easy way to look at that wiring is the ECG."

**2. The question (0:15 to 0:40)**
VISUAL: the heart seen through a foggy overlay; a magnifier tries to trace fine branches and cannot.
NARRATION: "But the ECG is a blurry, far-away view. It is like watching a fireworks show through fog. So we asked a question the field usually hand-waves: from that view, how much of the wiring can you actually recover, and how much is genuinely impossible to know?"

**3. What we built (0:40 to 1:05)**
VISUAL: the pipeline strip animates, theta to Purkinje tree to 12-lead ECG to the neural posterior estimator to a posterior distribution.
NARRATION: "We built an AI that reads an ECG and does not just guess one answer. It returns a range of possibilities with a confidence level, like a weather forecast. And we rigorously tested that its confidence is honest, because a seventy-percent forecast only means something if it rains seventy percent of the time."

**4. The finding (1:05 to 1:35)**
VISUAL: the identifiability spectrum bars fill in, delta_iv pinned green, branch_angle and w grey and unknowable. Then a "before calibration" overlay shows them looking recoverable, then snapping to unknowable.
NARRATION: "Here is the map. The ECG pins down the timing between the two sides of the heart, exactly what CRT therapy cares about. But the fine branching is fundamentally invisible. And crucially, before we ran the honesty check, some of those invisible settings looked recoverable. Calibration is what revealed the illusion."

**5. The honesty result (1:35 to 2:05)**
VISUAL: a metric flashes a near-perfect match, a red "HOLD" stamp lands, then the honest fidelity chart shows 0.20 rising to 0.79 with a labeled residual.
NARRATION: "While doing this, we almost fooled ourselves. A quick metric made it look like our simulator perfectly matched a real patient's ECG. A verification pass caught that the metric was cheating. So instead of claiming we solved it, we measured exactly where our simulator still diverges from reality, and we published that gap as a result."

**6. Why it matters + reuse (2:05 to 2:40)**
VISUAL: the Strocchi heart rotates next to crtdemo; a terminal shows `conduction-lens run`; a container icon.
NARRATION: "Digital twins of the heart are becoming real tools for planning therapy. A twin is only safe if it knows what it cannot infer and is honest about it. We built that honesty layer, on public anatomy, packaged so anyone can run it themselves."

**7. Close (2:40 to 3:00)**
VISUAL: the two-line thesis on a dark card, then "Built with Claude" and the verification-culture line.
NARRATION: "So the result is two parts: a trustworthy map of what an ECG can recover, and an honest measurement of where our model still falls short of a real heart. The moment that made it good science was refusing a metric that was too good to be true."

---
Honesty guardrails: never say "validated on real ECGs" or "solved". Keep the synthetic-truth framing. crtdemo is a model rig; "public anatomy" only over the Strocchi shot.
