import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import defaultdict


def _series(rows, suite, family=None, fam_prefix=None):
    out = defaultdict(list)
    for r in rows:
        if r["suite"] != suite: continue
        if family and r["family"] != family: continue
        if fam_prefix and not r["family"].startswith(fam_prefix): continue
        out[(r["algorithm"], r["family"])].append((r["n"], r["ops"], r["budget_hit"]))
    return out


def _plot(rows, suite, title, path, family=None, fam_prefix=None, xlabel="n", logx=True, ylabel="operations (log)"):
    fig, ax = plt.subplots(figsize=(6.4, 4))
    for (alg, fam), pts in _series(rows, suite, family, fam_prefix).items():
        pts.sort()
        ax.plot([p[0] for p in pts], [max(p[1], 1) for p in pts], marker="o", ms=3, label=f"{alg} [{fam}]" if not family else alg)
        for n, o, b in pts:
            if b: ax.plot(n, o, "rx", ms=9)
    ax.set_yscale("log")
    if logx: ax.set_xscale("log")
    ax.set_title(title, fontsize=10); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.grid(alpha=.3, which="both"); ax.legend(fontsize=6.5)
    fig.tight_layout(); fig.savefig(path, dpi=140); plt.close(fig)


def make_all(rows, aux, outdir):
    os.makedirs(outdir, exist_ok=True)
    p = lambda f: os.path.join(outdir, f)
    for fam, t in (("insert_then_extract_all", "Heaps: n inserts + n extract-mins"), ("decrease_key_storm", "Heaps: decrease-key storm"),
                   ("merge_chain", "Heaps: merge chain")):
        _plot(rows, "heaps", t, p(f"heaps_{fam}.png"), family=fam)
    for kind in ("ascending", "random"):
        _plot(rows, "trees", f"B-Tree(t=8) vs Red-Black: {kind} inserts + searches", p(f"trees_{kind}.png"), family=f"{kind}_insert+search")
    _plot(rows, "mst", "MST: sparse graphs", p("mst_sparse.png"), family="sparse_E=2V", xlabel="V")
    _plot(rows, "mst", "MST: dense graphs", p("mst_dense.png"), family="dense_E=0.8*Vmax", xlabel="V")
    _plot(rows, "mst", "MST: decrease-key adversary", p("mst_adversary.png"), family="decrease_key_adversary", xlabel="V")
    _plot(rows, "knapsack", "Knapsack: capacity stress (n=100)", p("knap_capacity.png"), family="capacity_stress(n=100)", xlabel="W")
    _plot(rows, "knapsack", "Knapsack: item stress (W=1000)", p("knap_items.png"), family="item_stress(W=1000)", xlabel="n")
    _plot(rows, "dp", "Floyd-Warshall vs V", p("fw.png"), fam_prefix="", xlabel="V") if False else None
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.8))
    for (alg, fam), pts in _series(rows, "dp").items():
        pts.sort(); a = ax[0] if alg == "floyd_warshall" else ax[1]
        a.plot([x[0] for x in pts], [x[1] for x in pts], marker="o", ms=3, label=fam)
    for a, t in zip(ax, ("Floyd-Warshall (V^3)", "Matrix Chain (n^3)")):
        a.set_xscale("log"); a.set_yscale("log"); a.set_title(t, fontsize=10); a.grid(alpha=.3, which="both"); a.legend(fontsize=7); a.set_xlabel("size")
    ax[0].set_ylabel("operations (log)"); fig.tight_layout(); fig.savefig(p("dp.png"), dpi=140); plt.close(fig)
    for alg, t, f in (("n_queens", "N-Queen: states generated", "search_nqueens.png"),
                      ("hamiltonian_backtracking", "Hamiltonian cycle: states generated", "search_ham.png")):
        fig, ax = plt.subplots(figsize=(6.4, 4))
        for (a, fam), pts in _series(rows, "search").items():
            if a != alg: continue
            pts.sort(); ax.plot([x[0] for x in pts], [max(x[1], 1) for x in pts], marker="o", ms=3, label=fam)
            for n, o, b in pts:
                if b: ax.plot(n, o, "rx", ms=9)
        ax.set_yscale("log"); ax.set_title(t, fontsize=10); ax.set_xlabel("n"); ax.set_ylabel("states (log)"); ax.grid(alpha=.3, which="both"); ax.legend(fontsize=7)
        fig.tight_layout(); fig.savefig(p(f), dpi=140); plt.close(fig)
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True)
    for ax, kind in zip(axs, ("euclidean", "uniform", "flat")):
        for (a, fam), pts in _series(rows, "search").items():
            if a.startswith("tsp") and fam == kind:
                pts.sort(); ax.plot([x[0] for x in pts], [x[1] for x in pts], marker="o", ms=3, label=a)
                for n, o, b in pts:
                    if b: ax.plot(n, o, "rx", ms=9)
        ax.set_yscale("log"); ax.set_title(f"TSP states - {kind} costs", fontsize=10); ax.set_xlabel("cities n"); ax.grid(alpha=.3, which="both"); ax.legend(fontsize=7)
    axs[0].set_ylabel("states generated (log)"); fig.tight_layout(); fig.savefig(p("search_tsp.png"), dpi=140); plt.close(fig)


def architecture(path):
    fig, ax = plt.subplots(figsize=(11, 5.2)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 5.2)
    def box(x, y, w, h, txt, c):
        ax.add_patch(plt.Rectangle((x, y), w, h, fc=c, ec="#333", lw=1.2)); ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=8)
    def arrow(x1, y1, x2, y2): ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="->", lw=1.4))
    box(.1, 3.7, 1.9, 1.1, "INPUT\nalgorithm / suite name\nsize range, seed, budget", "#e8f1fb")
    box(2.5, 3.7, 2.1, 1.1, "TEST-FAMILY GENERATORS\nnormal | large | boundary |\ndifficult (adversarial)", "#fdf0d5")
    box(5.1, 3.7, 2.4, 1.1, "ALGORITHM / DATA-STRUCTURE\nREGISTRY (all 16 syllabus topics)\nlab.py  ->  suites.py", "#e6f4ea")
    box(8.0, 3.7, 2.9, 1.1, "INSTRUMENTED EXECUTION\ncounters: comparisons, links, cuts,\nrotations, splits, states, pruned,\nqueue size", "#e6f4ea")
    box(.1, 1.9, 2.4, 1.1, "MEASUREMENT\nops | wall-time | memory\n(tracemalloc + structural units)", "#fde7e9")
    box(3.0, 1.9, 2.5, 1.1, "GROWTH ANALYSIS\nlocal log-log exponents,\nbudget / spike / erratic checks", "#fde7e9")
    box(6.0, 1.9, 2.3, 1.1, "RISK CLASSIFIER\nLow | Moderate | High", "#f3e5f5")
    box(8.8, 1.9, 2.1, 1.1, "EXPLANATION / OUTPUT\nrisk_report.csv, plots,\ntheory vs measured", "#f3e5f5")
    box(2.5, .2, 6.0, .9, "COMPLEXITY KNOWLEDGE BASE: decision vs optimization form,\nNP-Hard / NP-Complete / P / pseudo-polynomial, time & space bounds", "#eeeeee")
    for a in ((2.0, 4.25, 2.5, 4.25), (4.6, 4.25, 5.1, 4.25), (7.5, 4.25, 8.0, 4.25), (9.4, 3.7, 1.3, 3.0), (2.5, 2.45, 3.0, 2.45),
              (5.5, 2.45, 6.0, 2.45), (8.3, 2.45, 8.8, 2.45), (5.5, 1.1, 7.0, 1.9)):
        arrow(*a)
    ax.set_title("Framework architecture: input -> modelling -> selection -> execution -> measurement -> explanation", fontsize=10)
    fig.savefig(path, dpi=150, bbox_inches="tight"); plt.close(fig)
