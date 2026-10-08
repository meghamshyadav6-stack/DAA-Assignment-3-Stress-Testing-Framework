"""Risk classifier: Low / Moderate / High from MEASURED growth (not from labels)."""
import math


def _local_exponents(ns, ops):
    """Local log-log slopes between consecutive points."""
    out = []
    for i in range(1, len(ns)):
        if ops[i] > 0 and ops[i - 1] > 0 and ns[i] != ns[i - 1]:
            out.append(math.log(ops[i] / ops[i - 1]) / math.log(ns[i] / ns[i - 1]))
    return out


def classify_series(ns, ops, budget_hit=False, pseudo_poly=False, spike_ratio=None):
    """Returns dict(risk, model, p_first, p_last, erratic, reason).
    HIGH      : budget exhausted, or growth is super-polynomial (local exponent keeps climbing: p_last>=5 and p_last>=1.6*p_first)
    MODERATE  : polynomial exponent >= 2.5, or pseudo-polynomial in a numeric input, or latency spike >= 100x mean,
                or erratic (instance-dependent) growth (a >25% DROP in cost as size increases)
    LOW       : otherwise."""
    pts = sorted(zip(ns, ops))
    ns, ops = [p[0] for p in pts], [p[1] for p in pts]
    exps = _local_exponents(ns, ops)
    p_first = exps[0] if exps else 0.0
    p_last = exps[-1] if exps else 0.0
    p_mean = sum(exps) / len(exps) if exps else 0.0
    erratic = any(ops[i] < 0.75 * ops[i - 1] for i in range(1, len(ops)))
    superpoly = (not erratic) and len(exps) >= 3 and p_last >= 5 and p_last >= 1.6 * p_first
    if budget_hit or superpoly:
        risk, model = "High", "super-polynomial / budget exhausted"
        reason = ("state budget exhausted - exact search impractical beyond tested size" if budget_hit else
                  f"local growth exponent climbs {p_first:.1f} -> {p_last:.1f} (not a fixed polynomial)")
    elif pseudo_poly:
        risk, model = "Moderate", f"polynomial in numeric value (exponent ~{p_mean:.2f})"
        reason = "cost scales with the numeric capacity W, i.e. exponentially in its bit-length"
    elif erratic:
        risk, model = "Moderate", "irregular / instance dependent"
        reason = "cost is not monotone in size - heavy-tailed, depends on instance luck"
    elif p_last >= 2.5:
        risk, model = "Moderate", f"polynomial, exponent ~{p_last:.2f}"
        reason = "high-degree polynomial: fine for hundreds, costly for thousands of items"
    elif spike_ratio is not None and spike_ratio >= 100:
        risk, model = "Moderate", f"polynomial, exponent ~{p_mean:.2f} but latency spikes"
        reason = f"a single operation costs {spike_ratio:.0f}x the average (amortized bound hides worst-case latency)"
    else:
        risk, model = "Low", f"polynomial, exponent ~{p_mean:.2f}"
        reason = "growth matches the expected low-degree trend"
    return {"risk": risk, "model": model, "p_first": round(p_first, 2), "p_last": round(p_last, 2),
            "p_mean": round(p_mean, 2), "erratic": erratic, "reason": reason}
