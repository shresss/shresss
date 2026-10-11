"""Study 2 power simulation: can N items separate models as close as Study 1's top four?

Study 1 fact this rests on: the top four models finished within 3 of 204 cases
(about 1.5 points from #1 to #4, about 0.5 points between neighbours).

Generative model (logit scale), per model j, title t, item i:
    correct ~ Bernoulli(logistic(a_j + u_t + v_i + w_jt))
    u_t  ~ N(0, sd_title)   title difficulty, shared by all models
    v_i  ~ N(0, sd_item)    item difficulty, shared by all models
    w_jt ~ N(0, sd_mxt)     model-by-title interaction (a model is better on
                            some titles); this is what makes title clustering matter
a_j is solved so each model's expected accuracy hits its target.

Test: paired difference between two models, cluster-robust SE with titles as
clusters (items from one title are not independent draws). Reported power is
the share of simulated studies where the 95% interval excludes zero AND the
sign is right. "bonf15" uses the threshold for 15 pairwise tests (6 models).

Replace the assumptions with pilot estimates: the printed discordance rate
(share of items where exactly one of the two models is right) is the number
to match against the pilot.

Usage: python3 power_sim.py [--sims 2000] [--seed 20261011]
"""

import argparse
import math

import numpy as np

Z_95 = 1.959964
Z_BONF15 = 2.935199  # two-sided 0.05 / 15


def logistic(x):
    return 1.0 / (1.0 + np.exp(-x))


def solve_intercept(target, sd_total, rng, n=400_000):
    """Find a with E[logistic(a + N(0, sd_total))] == target."""
    z = rng.standard_normal(n) * sd_total
    lo, hi = -10.0, 10.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if logistic(mid + z).mean() < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def simulate(accs, n_titles, per_title, sd_title, sd_item, sd_mxt, sims, rng):
    """Return per-sim (scores matrix [sims, models], title-level diff sums for pair 0-1 and 0-3)."""
    k = len(accs)
    sd_total = math.sqrt(sd_title**2 + sd_item**2 + sd_mxt**2)
    a = np.array([solve_intercept(p, sd_total, rng) for p in accs])
    n = n_titles * per_title

    scores = np.empty((sims, k))
    z01 = np.empty(sims)
    z03 = np.empty(sims)
    disc01 = np.empty(sims)
    disc03 = np.empty(sims)
    for s in range(sims):
        u = rng.standard_normal(n_titles) * sd_title
        v = rng.standard_normal((n_titles, per_title)) * sd_item
        w = rng.standard_normal((k, n_titles)) * sd_mxt
        logit = a[:, None, None] + u[None, :, None] + v[None, :, :] + w[:, :, None]
        x = rng.random(logit.shape) < logistic(logit)  # [k, titles, per_title]
        scores[s] = x.reshape(k, -1).mean(axis=1)
        for (j, zs, ds) in ((1, z01, disc01), (3, z03, disc03)):
            if j >= k:
                zs[s] = ds[s] = np.nan
                continue
            d = x[0].astype(np.int8) - x[j].astype(np.int8)  # [titles, per_title]
            dt = d.sum(axis=1)
            mean = dt.sum() / n
            resid = dt - per_title * mean
            se = math.sqrt(n_titles / (n_titles - 1) * (resid**2).sum()) / n
            zs[s] = mean / se if se > 0 else 0.0
            ds[s] = (d != 0).mean()
    return scores, z01, z03, disc01, disc03


def power(z):
    return float((z > Z_95).mean()), float((z > Z_BONF15).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sims", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261011)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    top = 0.85
    accs = [top, top - 0.005, top - 0.010, top - 0.015]  # Study 1-like spread
    scenarios = {
        # name: (sd_title, sd_item, sd_mxt)
        "low-heterogeneity": (0.5, 1.0, 0.0),
        "high-heterogeneity": (1.0, 2.0, 0.0),
        "high-het + model-x-title": (1.0, 2.0, 0.4),
        # items nearly decide themselves: top models disagree on ~6-8% of items
        "high-agreement": (1.5, 5.0, 0.0),
    }
    designs = [
        ("Study 1 size (204, ~1/title)", 204, 1),
        ("main, public only (186 x 4)", 186, 4),
        ("main as drafted (186 x 5)", 186, 5),
        ("186 x 10", 186, 10),
        ("186 x 20", 186, 20),
    ]

    print(f"accuracies: {accs}  (#1 vs #2 gap 0.5pt, #1 vs #4 gap 1.5pt)")
    print(f"sims per cell: {args.sims}, seed {args.seed}\n")
    hdr = (f"{'design':32s} {'n':>5s}  {'disc 1v4':>8s}  {'pow 1v2':>7s}  "
           f"{'pow 1v4':>7s}  {'1v4 bonf':>8s}  {'P(#1 first)':>11s}")
    for name, (st, si, sm) in scenarios.items():
        print(f"== {name}: sd_title={st} sd_item={si} sd_model_x_title={sm}")
        print(hdr)
        for label, t, m in designs:
            scores, z01, z03, _, d03 = simulate(accs, t, m, st, si, sm, args.sims, rng)
            p12, _ = power(z01)
            p14, p14b = power(z03)
            first = float((scores.argmax(axis=1) == 0).mean())
            print(f"{label:32s} {t*m:5d}  {d03.mean():8.3f}  {p12:7.2f}  "
                  f"{p14:7.2f}  {p14b:8.2f}  {first:11.2f}")
        print()

    print("What 930 items can detect (#1 vs #2, high-agreement, 80% power target):")
    st, si, sm = scenarios["high-agreement"]
    for gap in (0.02, 0.03, 0.04):
        _, z01, _, d01, _ = simulate([top, top - gap], 186, 5, st, si, sm, args.sims, rng)
        p, pb = power(z01)
        print(f"  gap {gap*100:.0f}pt: disc {d01.mean():.3f}  power {p:.2f}  bonf15 {pb:.2f}")
    print()

    print("Analytic check (no clustering): n for 80% power, two-sided 0.05,")
    print("n = (1.96 + 0.84)^2 * discordance / gap^2")
    for disc in (0.05, 0.08, 0.12):
        for gap in (0.005, 0.015, 0.03):
            n = (Z_95 + 0.841621) ** 2 * disc / gap**2
            print(f"  discordance {disc:.2f}, gap {gap*100:.1f}pt -> n = {n:,.0f}")


if __name__ == "__main__":
    main()
