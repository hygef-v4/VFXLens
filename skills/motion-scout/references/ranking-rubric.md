# Evidence-weighted selection

Apply license and security eligibility before recommending executable reuse.
Eligibility is `eligible`, `conditional/reference-only`, or `rejected`, with a
reason. An absent/unclear license is not permission to copy; it may still permit
conceptual study. Unsafe execution or incompatible reuse requirements fail the
proposed integration even when the visuals are attractive.

| Dimension | Weight | Evidence that earns confidence |
| --- | --- | --- |
| Visual quality / innovation | 30% | Actually viewed demo frames/motion; relevant look, clarity, depth and novelty |
| Demonstrated implementation | 25% | Real relevant source plus demonstrated output; local reproduction is stronger |
| Reuse / video compatibility | 20% | Small separable unit, installed APIs, arbitrary-frame state and capture path |
| Engineering / maintenance | 15% | Ownership, error paths, tests/docs, dependency hygiene and relevant activity |
| Verified recent momentum | 10% | Dated historical metrics/window; source and limitations explicit |

Optional scoring uses 0–5 per dimension with a written reason and evidence for
each rating; `sum(weight * rating / 5)` yields 0–100. Use a numeric overall score
only when all five dimensions have adequate evidence. Unknown does not become
zero or a guessed midpoint. Otherwise give a qualitative, explicitly provisional
tier with missing dimensions and confidence. No false decimals or star-age proxy.

- **S:** exceptional fit, strong viewed visual and implementation evidence,
  clear reuse strategy and passed eligibility gates.
- **A:** strong useful selection; explain any integration/testing condition.
- **B:** valuable specialized technique with material adaptation/uncertainty.
- **C:** reference/discovery value; weak direct fit or insufficient reuse evidence.
- **Rejected:** unsupported, unsafe, unusable, or legally incompatible for the
  proposed use. State the exact failed gate; avoid universal judgments.

Keep labels independent from tiers:

- **Verified Viral:** observed windowed attention supports the explicitly stated
  “meaningful recent attention” rule in this report. Show the actual numbers/window.
- **Reported Viral:** a named source reports attention; underlying history is not
  independently verified.
- **Exceptional:** technical/visual judgment supported by the inspected evidence,
  regardless of popularity. Mark it provisional if a relevant dimension is unknown.
- **Experimental:** maturity, backend or repeatability remains risky/unverified.

Describe observed failures separately from suspected risks. A real-time particle
system can be excellent interactive technology and still need baking/replay for
Remotion. Do not equate technical sophistication, a polished README or a tier
with a validated local video render. Choose complementary winners, not one winner
per category when the brief needs fewer tools.
