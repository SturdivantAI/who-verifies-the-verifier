"""Exact Krippendorff's alpha for the GLM-5.2 verdict corpus.

Input: CSV with 5,081 rows and columns
    claim_id, verified, falsified, inconclusive, toy   (four integer counts; row sum = m)
Optional extra column `orid` enables the by-paper breakout.

Runs: exact coincidence-matrix alpha, bootstrap CI over claims, alpha by m-band,
severity-weighted alpha, and the Blocker-1 hard-contradiction count.
"""
import numpy as np, pandas as pd

CATS = ["verified", "falsified", "inconclusive", "toy"]
VI, FI = 0, 1  # indices of the two poles that constitute a hard contradiction


def contributions(counts):
    """Per-unit coincidence contributions, flattened to (n_units, 16).
    Summing any subset of rows and reshaping to (4,4) gives that subset's
    coincidence matrix -- which makes the bootstrap a matrix multiply."""
    c = np.asarray(counts, float)
    m = c.sum(1)
    keep = m >= 2                      # units judged once carry no reliability information
    c, m = c[keep], m[keep]
    w = 1.0 / (m - 1.0)
    outer = c[:, :, None] * c[:, None, :]              # (u,4,4)
    idx = np.arange(4)
    outer[:, idx, idx] -= c                            # subtract the diagonal self-pairs
    return (outer * w[:, None, None]).reshape(len(c), 16)


def coincidence(counts):
    """Krippendorff coincidence matrix from per-unit category counts (n_units x 4)."""
    return contributions(counts).sum(0).reshape(4, 4)


def alpha_from_O(O, delta=None):
    """alpha for a given coincidence matrix and metric. delta=None -> nominal."""
    if delta is None:
        delta = 1.0 - np.eye(4)
    n = O.sum()
    nc = O.sum(1)
    E = np.outer(nc, nc) - np.diag(nc)
    D_o = (O * delta).sum() / n
    D_e = (E * delta).sum() / (n * (n - 1.0))
    return 1.0 - D_o / D_e, D_o, D_e


def severity_delta(hard=1.0, soft=0.5):
    """verified<->falsified is a hard contradiction; anything touching
    inconclusive/toy is a confidence shift and penalised less."""
    d = np.full((4, 4), soft)
    np.fill_diagonal(d, 0.0)
    d[VI, FI] = d[FI, VI] = hard
    return d


def blocker1(counts):
    """claims carrying at least one verified<->falsified pair"""
    c = np.asarray(counts)
    return int(((c[:, VI] > 0) & (c[:, FI] > 0)).sum())


def bootstrap_ci(counts, delta=None, B=10000, seed=0, chunk=1000):
    """Nonparametric bootstrap resampling CLAIMS (the unit of analysis).
    Resampling units == reweighting their coincidence contributions, so each
    replicate is a multinomial draw times the contribution matrix."""
    rng = np.random.default_rng(seed)
    contrib = contributions(counts)
    n = len(contrib)
    out = np.empty(B)
    done = 0
    while done < B:
        b = min(chunk, B - done)
        W = rng.multinomial(n, np.full(n, 1.0 / n), size=b).astype(float)
        Os = (W @ contrib).reshape(b, 4, 4)
        for i in range(b):
            out[done + i] = alpha_from_O(Os[i], delta)[0]
        done += b
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def run(path):
    df = pd.read_csv(path)
    c = df[CATS].to_numpy(int)
    m = c.sum(1)
    rep = m >= 2
    res = {}

    a, D_o, D_e = alpha_from_O(coincidence(c))
    res["alpha_nominal"] = a
    res["D_o"] = D_o
    res["D_e"] = D_e
    res["alpha_nominal_CI"] = bootstrap_ci(c[rep])

    sd = severity_delta()
    a_s, Do_s, De_s = alpha_from_O(coincidence(c), sd)
    res["alpha_severity"] = a_s
    res["alpha_severity_CI"] = bootstrap_ci(c[rep], sd)

    bands = {"m=2": m == 2, "m=3-5": (m >= 3) & (m <= 5),
             "m=6-10": (m >= 6) & (m <= 10), "m>10": m > 10}
    res["by_band"] = {k: (int(v.sum()), alpha_from_O(coincidence(c[v]))[0]) for k, v in bands.items()}

    nb = blocker1(c)
    res["blocker1_n"] = nb
    res["blocker1_pct"] = 100.0 * nb / rep.sum()
    res["n_claims"] = int(rep.sum())
    res["n_instances"] = int(m[rep].sum())
    res["any_disagreement_pct"] = 100.0 * float((c[rep].max(1) < m[rep]).mean())
    return res


# ---- implementation self-tests (structure only; no corpus values involved) ----
if __name__ == "__main__":
    perfect = np.array([[4, 0, 0, 0], [0, 3, 0, 0], [0, 0, 2, 0]])
    assert abs(alpha_from_O(coincidence(perfect))[0] - 1.0) < 1e-12, "perfect agreement must give alpha=1"

    # hand-computable: two units, m=2, one agreeing (verified,verified), one split (verified,falsified)
    hand = np.array([[2, 0, 0, 0], [1, 1, 0, 0]])
    O = coincidence(hand)
    assert abs(O.sum() - 4.0) < 1e-12
    a, D_o, D_e = alpha_from_O(O)
    # D_o = 2 disagreeing cells / 4 = 0.5 ; marginals (3,1) -> D_e = (2*3*1)/(4*3) = 0.5 ; alpha = 0
    assert abs(D_o - 0.5) < 1e-12 and abs(D_e - 0.5) < 1e-12 and abs(a) < 1e-12, (D_o, D_e, a)

    # random assignment at scale must give alpha ~ 0
    rng = np.random.default_rng(1)
    p = np.array([0.535, 0.044, 0.221, 0.200])
    big = np.array([np.bincount(rng.choice(4, size=5, p=p), minlength=4) for _ in range(4000)])
    a_rand = alpha_from_O(coincidence(big))[0]
    assert abs(a_rand) < 0.03, a_rand

    assert blocker1(np.array([[1, 1, 0, 0], [2, 0, 0, 0], [0, 1, 1, 0]])) == 1
    print(f"self-tests passed (random-data alpha = {a_rand:+.4f})")
