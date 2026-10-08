"""Fractional knapsack (greedy), 0/1 knapsack (DP, pseudo-polynomial) and the
ratio-greedy heuristic applied (wrongly) to the 0/1 problem."""
from .util import counted_sorted


def _ratio(it):
    v, w = it
    return float("inf") if w == 0 else v / w


def fractional_knapsack(items, W):
    """items: list of (value, weight). Returns (value, stats). O(n log n)."""
    order, cmp = counted_sorted(items, key=_ratio, reverse=True)
    cap, val, scans = W, 0.0, 0
    for v, w in order:
        scans += 1
        if cap <= 0:
            break
        if w <= cap:
            val += v
            cap -= w
        else:
            val += v * cap / w
            cap = 0
    return val, {"ops": cmp + scans, "sort_comparisons": cmp}


def greedy_01(items, W):
    """Ratio-greedy WITHOUT splitting - a heuristic, not optimal for 0/1."""
    order, cmp = counted_sorted(items, key=_ratio, reverse=True)
    cap, val = W, 0
    for v, w in order:
        if w <= cap:
            val += v
            cap -= w
    return val, {"ops": cmp + len(items)}


def knapsack_01(items, W, keep_table=False):
    """Bottom-up DP. ops = number of table-cell updates (exactly sum(W-w+1))."""
    dp = [0] * (W + 1)
    cells = 0
    keep = [] if keep_table else None
    for v, w in items:
        row = bytearray(W + 1) if keep_table else None
        for c in range(W, w - 1, -1):
            cells += 1
            cand = dp[c - w] + v
            if cand > dp[c]:
                dp[c] = cand
                if row is not None:
                    row[c] = 1
        if keep_table:
            keep.append(row)
    chosen = None
    if keep_table:
        chosen, c = [], W
        for i in range(len(items) - 1, -1, -1):
            if keep[i][c]:
                chosen.append(i)
                c -= items[i][1]
        chosen.reverse()
    return dp[W], chosen, {"ops": cells, "table_cells": len(items) * (W + 1) if keep_table else W + 1}
