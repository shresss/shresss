# Study 2 plan, stress-tested from the handoff

Written 11 Oct 2026 in a cloud session that **cannot see the study files**. `study2/`,
`~/Downloads/study2-sandbox`, the Study 1 key and the publication repo are all on the
local machine. Everything below comes from the handoff text, not from the items. Every
"check" is a check to run once the files are reachable. The one thing run here is
`power_sim.py`: seeded, assumption-driven, output in `power_sim_output.txt`.

## 1. Verdict

The core design holds up: two writers from different model families, labels
cross-checked by the other family, two wording sets, padded long versions, a private
split, and a runner that pins model versions and stops at a cost cap. It is more
auditable than anything Recruitly publishes.

Three problems must be fixed before the pilot:

1. **930 items cannot rank Study 1's top four.** The design can find tiers, not an
   order within the top tier. Pre-register tiers, or quadruple the items (§2).
2. **The invariants were never checked against the Study 1 key.** They came from
   agents that never saw the cases (correct for leakage), so a title whose invariant
   differs from the rule your Study 1 answers used would measure something else.
   DC34 and DC138 were caught because the agents noticed ambiguity. A silent
   mismatch would not have been (F2).
3. **The "clearly Strong / clearly Unusable" fix for DC138 makes items easier than
   Study 1's.** Easier items push every model toward the ceiling, and then nothing
   separates (F3).

## 2. Power: what Study 2 can and cannot claim

Assumptions: the top model at 85%; the next three 0.5, 1.0 and 1.5 points below it
(Study 1's top four were within 3 of 204 cases, about 1.5 points). Tests are paired,
with titles as clusters. 1,500 simulations per cell. The ranges below cover four
scenarios for how often the top models disagree on an item (9% to 23%).

| Design | n | Power, #1 vs #2 (0.5pt) | Power, #1 vs #4 (1.5pt) | Same, corrected for 15 pairs | P(true #1 ranks first) |
|---|---|---|---|---|---|
| Study 1 size | 204 | 3–5% | 6–11% | 1% | 38–49% |
| 186 × 4 (public only) | 744 | 4–7% | 13–29% | 2–6% | 48–60% |
| **186 × 5 (as drafted)** | **930** | **5–9%** | **16–37%** | **3–9%** | **51–70%** |
| 186 × 10 | 1,860 | 7–11% | 28–57% | 5–21% | 59–75% |
| 186 × 20 | 3,720 | 8–24% | 47–89% | 14–60% | 68–90% |

What 930 items can detect, in the most favourable scenario (top models disagree on
about 9% of items): a **3-point gap at 86% power**, falling to 56% once corrected for 15
pairs. A **4-point gap at 97%** (82% corrected). Anything under 2 points is a coin flip.

What this means:

- **Study 1's order within the top four is not evidence of an order.** Even if those
  gaps are real, a 204-case study puts the true #1 first only 38–49% of the time. So
  "did Study 1's order replicate?" is the wrong question for Study 2: even if Study 1
  is right, Study 2 reproduces its #1 only 51–70% of the time.
- **Decision (recommended): claim tiers, not ranks.** That is the defensible claim,
  and it is the thing a confidence-interval-free leaderboard can't offer.
- If you want ranks inside the top tier, you need about 16–20 items per title (3,000 to
  3,700). Model cost is trivial. The cost is your adjudication time, which grows with n
  (see F8).

Rerun `power_sim.py` with the pilot's measured disagreement rate before sizing the main run.

## 3. Fixes before the pilot, most severe first

**F1. Pre-register tiers (§4).** Do not let the post imply an order the data can't
support.

**F2. Invariant audit against the Study 1 key.** A fresh agent sees, for each title,
the Study 1 answer key, the rationale and the invariant. It writes no item text, so
nothing leaks. It returns MATCH, MISMATCH or AMBIGUOUS with one line of reasoning. You
resolve every non-MATCH. Do the 40 pilot titles first, then all 186 before Codex
(Writer B) writes the main batch.

**F3. Settle the cutoff before writing, and match Study 1's difficulty.**
- Pick the 1.5 cutoff or each title's own threshold now. Items that sit clearly on one
  side fit any threshold only because they are easy.
- Tell the writers to match Study 1's share of near-cutoff items, keeping any item
  where rounding could flip the label out of the set.
- Pilot gate: compare each family's accuracy for the same models in Study 1 and
  Study 2. If every model gains 10 points or more on a family, that family's items are
  too easy, so revise the spec. Also, if the top model scores more than 5 points above
  its Study 1 accuracy overall, the items are too easy.

**F4. Review all 150 padding blocks, not 30.** Zero defects in 30 still leaves a 95%
upper bound of about 9.5%, roughly 14 bad blocks. Each block is reused across many
long items, so one bad block silently flips labels in all of them. 150 short blocks is
about an hour.

**F5. Balance arithmetic.** 930 = 186 × 5, and five items cannot split evenly across
four writer × wording cells (930 / 4 = 232.5). Recommended layout: 4 public items per
title, one per cell (744 items, exactly balanced per title), plus 1 private item per
title (186 items, cells 47/47/46/46). Check which layout the seeded assignments
actually encode. The handoff's "930 with one per title held back" reads either way.

**F6. Commit to the private split by hash.** Before posting, publish the SHA-256 of
the private split file and of each item in the public repo and in the post. A later
reveal is then verifiable, and nobody can say the split was chosen after the fact.

**F7. Partial outputs from the four interrupted agents.** Run the checker plus count
checks (150 padding blocks, 40 Writer A pilot items, both wording sets complete). For
any agent whose output is incomplete, regenerate its whole task from the same spec and
seed. Never fill gaps by hand, because writer identity is a variable. Log each
regeneration in `STATUS.md`.

**F8. Use the pilot for the pipeline, not for sizing.**
- What 80 items can't settle: the top-pair disagreement rate. At about 9% it has a 95%
  interval of roughly 3–15%, and the n needed for a 1.5-point gap swings from about
  1,000 to about 5,000 across that range.
- What the pilot should measure: label disagreement rate, hard fails, cost, difficulty
  against Study 1, and how often answers flip between runs.
- Label disagreement rate × main n = your adjudication load. At 20% that is about 186
  decisions for 930 items, and about 740 for 3,700.

**F9. Pilot cost check.**
- "Under $1" for 6 models × 3 runs × 80 items × 2 lengths (2,880 calls) means under
  $0.00035 a call. That holds only if all six models are cheap. One frontier model on
  long prompts of a few thousand tokens costs several dollars by itself.
- Before running, recompute the estimate from the assembled items' real token counts
  and list prices, and set the cap at 1.5 × that estimate.
- Have the runner loop over items with all models inside each item, so a cap stop
  leaves a balanced partial run rather than three models done and three never run.

**F10. Hygiene.**
- Pilot items stay out of the main analysis.
- Freeze the writer spec (hash it) before the pilot.
- Never pool short and long versions as 2n: they are the same items. The primary
  ranking uses short versions only, the closest to Study 1. Long versions answer a
  separate, paired question: does length hurt?

## 4. Pre-registration: freeze, commit and hash before the main run

- **Primary outcome:** per-model accuracy on the public short items. An item's score
  is the mean over its 3 runs.
- **Interval:** paired cluster bootstrap with titles as clusters, 10,000 resamples,
  seeded.
- **Tier rule:** sort models by accuracy. Each model joins the tier of the model above
  it unless the 95% interval of their paired difference excludes 0, with a Holm
  correction across the adjacent pairs.
- **Study 1 is contradicted if:** a model in Study 1's top tier lands in a lower
  Study 2 tier, or a model outside it beats a Study 1 top-tier model with an interval
  that excludes 0. Agreement is claimed only if the tiers match. Publish whichever
  happens.
- **Secondary, descriptive, no claims of significance:**
  - accuracy by family
  - the length effect (long minus short, paired)
  - the run flip rate
  - rank by writer
  - a self-preference check: Claude models' Writer A minus Writer B accuracy, compared
    with the same difference for the other models
- **Labels:** each item records the writer's label, the other family's label, the
  final label and who decided. Your call is final. The data card reports disagreement
  rates by family and by writer.
- **Exclusions:** items the checker fails are fixed or dropped before any model runs.
  Never drop an item after results are in. Hard fails (unparseable output, refusal,
  timeout) count as wrong and are also reported separately.
- **Stops:** a model version change mid-run invalidates that model's run, which is
  rerun whole. The cost cap is as in F9.

## 5. "Parity with Recruitly": what it can and can't mean

I could not load recruitly.io from this session (blocked by the network policy).
Everything here comes from search snippets. Two snippets gave different top scores (100
vs 81), so the page changes over time. Cite it with a dated capture, made the same day
as your own Wayback capture.

| Recruitly publishes (per snippets) | You | Action |
|---|---|---|
| Quality score per model | Accuracy | ✓ Add intervals, which they don't show |
| Hard-fail count | ? | Check that the runner logs hard fails separately from wrong answers |
| Cost per task | Runner records usage and cost | ✓ |
| Latency, and latency against prompt length | ? | Log latency per call. Long versions give the length test for free |
| 24 models | 6 | Breadth is cheap: add low-cost models after the pilot |
| Scored on real production work | Synthetic items | **You can't match this. Don't claim it.** |

Don't write "parity" in the post. Write what you measure that they don't: published
labels, two writers from different model families, wording robustness, intervals, a
private split committed by hash, and the run flip rate.

## 6. Remaining steps, with gates

| # | Step | Owner | Gate to pass |
|---|---|---|---|
| 0 | Make the files reachable (§7) | You | Repo attached, or continue locally |
| 1 | Checker and count checks on the interrupted agents' outputs; regenerate incomplete tasks | Claude | Every count exact, checker clean |
| 2 | Invariant audit (F2); decide the cutoff (F3) and DC34; freeze the writer spec | Claude, then you | No unresolved MISMATCH |
| 3 | Review the 2 wording sets; Codex writes Writer B's pilot items and padding; **review all 150 padding blocks** | You | Every block signed off |
| 4 | Cross-labeling of pilot items; you adjudicate | Codex, Claude, you | Disagreement rate recorded |
| 5 | Assemble; recost from real tokens; set the cap; run the pilot with models interleaved | Claude | Estimate ≤ cap, balanced |
| 6 | Pilot analysis: hard fails, label disagreement, difficulty against Study 1, flip rate, top-pair disagreement; rerun `power_sim.py` | Claude | Difficulty gate (F3) passes |
| 7 | Choose tiers at 930 or scale to about 3,700; freeze §4 (commit and hash) | You | Pre-registration committed |
| 8 | Main run, then analysis exactly as pre-registered; publish the private split's hash | Claude | Done |

Still open from Part A: accept or reject DC11 and DC38; fix the "[1 to 3]" wording on
Jev's confident mistakes (7, 3 or 1 depending on the key); approve the public repo push;
run Save Page Now on posting day.

## 7. To continue in a cloud session

- **Files:** push the local study repo, including `study2/` and the sandbox outputs, to
  a **private** GitHub repo, then attach it to the session.
- **Keys for the pilot:** add each provider's API key as a secret in the environment's
  settings (cloud environment menu → Edit). Never paste a key into chat.
- **Network:** add each provider's API host to Allowed domains in the same menu. The
  current policy already blocked one outside host.
- **Codex (Writer B):** runs on your machine either way.
- **The simpler path:** after your limit resets, finish steps 1–5 locally, where the
  files and Codex already are, and use this plan as the checklist.
