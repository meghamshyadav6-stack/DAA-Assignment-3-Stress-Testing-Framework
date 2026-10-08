"""Experiment suites. Each suite returns (rows, aux).
row: dict(suite, algorithm, family, n, ops, time_s, status, budget_hit, extra{...})
aux: dict name -> list of dict (extra tables for the report)."""
import random
import time

from . import generators as G
from .ds_binomial import BinomialHeap
from .ds_btree import BTree
from .ds_fibonacci import FibonacciHeap
from .ds_rbtree import RBTree
from .dp import floyd_warshall, matrix_chain, left_to_right_cost
from .graphs import build_matrix, kruskal, prim_fibonacci, prim_matrix
from .knapsack import fractional_knapsack, greedy_01, knapsack_01
from .search import hamiltonian_cycle, n_queens, tsp_backtracking, tsp_branch_and_bound
from .util import measure


def row(suite, algorithm, family, n, ops, t, status="ok", **extra):
    return {"suite": suite, "algorithm": algorithm, "family": family, "n": n, "ops": ops,
            "time_s": round(t, 5), "status": status, "budget_hit": status != "ok", "extra": extra}


# --------------------------------------------------------------------- heaps
def suite_heaps(sizes=(250, 500, 1000, 2000, 4000, 8000)):
    rows = []
    for n in sizes:
        rnd = random.Random(n)
        keys = rnd.sample(range(10 * n), n)
        for name, H in (("binomial_heap", BinomialHeap), ("fibonacci_heap", FibonacciHeap)):
            # W1: n inserts, then extract everything (heap-sort pattern)
            h = H(track=True); t0 = time.perf_counter()
            for i, k in enumerate(keys): h.insert(k, i)
            w_ins = h.work(); worst = 0
            while len(h):
                b = h.work(); h.extract_min(); worst = max(worst, h.work() - b)
            tot = h.work(); avg = tot / (2 * n)
            rows.append(row("heaps", name, "insert_then_extract_all", n, tot, time.perf_counter() - t0,
                            insert_work=w_ins, max_single_op=worst, spike_ratio=round(worst / avg, 1)))
            # W2: decrease-key storm (Dijkstra / Prim-like)
            h = H(track=True)
            for i, k in enumerate(keys): h.insert(k, i)
            _, first = h.extract_min()
            live = sorted((k, i) for i, k in enumerate(keys) if i != first)
            b = h.work(); t0 = time.perf_counter(); worst = 0
            for r, (k, i) in enumerate(reversed(live), 1):
                bb = h.work(); h.decrease_key(i, -r); worst = max(worst, h.work() - bb)
            rows.append(row("heaps", name, "decrease_key_storm", n, h.work() - b, time.perf_counter() - t0,
                            max_single_op=worst, decrease_keys=len(live)))
            # W3: merge chain of n/8 small heaps
            parts = []
            for g in range(n // 8):
                p = H(); [p.insert(keys[g * 8 + j], g * 8 + j) for j in range(8)]; parts.append(p)
            base = parts[0]; b = base.work(); t0 = time.perf_counter()
            for p in parts[1:]: base.merge(p)
            merge_work = base.work() - b - sum(p.work() for p in parts[1:])
            rows.append(row("heaps", name, "merge_chain", n, max(merge_work, 1), time.perf_counter() - t0, merges=len(parts) - 1))
    return rows, {}


# --------------------------------------------------------------------- trees
def suite_trees(sizes=(1000, 2000, 4000, 8000, 16000, 32000), t_deg=8):
    rows, aux = [], {"btree_degree_sweep": [], "tree_height_check": []}

    def order(n, kind, rnd):
        if kind == "ascending": return list(range(n))
        if kind == "descending": return list(range(n, 0, -1))
        if kind == "zigzag": return [(i // 2 if i % 2 == 0 else n - i // 2) for i in range(n)]
        ks = list(range(n)); rnd.shuffle(ks); return ks

    for n in sizes:
        for kind in ("ascending", "descending", "zigzag", "random"):
            rnd = random.Random(n)
            keys = order(n, kind, rnd)
            queries = [rnd.randrange(-n // 4, n + n // 4) for _ in range(n // 2)]
            for name, T in (("b_tree", lambda: BTree(t=t_deg)), ("red_black_tree", RBTree)):
                tr = T(); t0 = time.perf_counter()
                for k in keys: tr.insert(k)
                ins = tr.work()
                for q in queries: tr.search(q)
                tot = tr.work()
                if name == "b_tree":
                    ex = dict(height=tr.height, splits=tr.stats["splits"], node_accesses=tr.stats["node_accesses"],
                              utilization=round(tr.utilization(), 3), nodes=tr.node_count, insert_work=ins)
                else:
                    ex = dict(height=tr.height(), rotations=tr.stats["rotations"], recolorings=tr.stats["recolorings"],
                              comparisons=tr.stats["comparisons"], insert_work=ins, nodes=tr.n)
                rows.append(row("trees", name, f"{kind}_insert+search", n, tot, time.perf_counter() - t0, **ex))
    # degree sweep (B-Tree) and RB height guarantee
    n = 16000
    ks = list(range(n)); random.Random(1).shuffle(ks)
    for t in (2, 3, 4, 8, 16, 32, 64):
        for kind, seq in (("random", ks), ("ascending", sorted(ks))):
            bt = BTree(t=t)
            for k in seq: bt.insert(k)
            aux["btree_degree_sweep"].append(dict(t=t, order=kind, height=bt.height, splits=bt.stats["splits"],
                                                  utilization=round(bt.utilization(), 3), nodes=bt.node_count))
    import math
    for n in (1000, 8000, 32000):
        for kind in ("ascending", "random"):
            rb = RBTree(); seq = list(range(n)) if kind == "ascending" else random.Random(2).sample(range(n), n)
            for k in seq: rb.insert(k)
            aux["tree_height_check"].append(dict(n=n, order=kind, rb_height=rb.height(), bound_2log2=round(2 * math.log2(n + 1), 1),
                                                 log2n=round(math.log2(n), 1)))
    return rows, aux


# ----------------------------------------------------------------------- mst
def suite_mst():
    rows = []
    plans = [("sparse_E=2V", [100, 200, 400, 800, 1600], G.sparse_graph),
             ("dense_E=0.8*Vmax", [50, 100, 200, 300, 400], G.dense_graph),
             ("decrease_key_adversary", [50, 100, 150, 200, 300], G.prim_decrease_adversary)]
    for fam, sizes, gen in plans:
        for V in sizes:
            E = gen(V)
            ref = None
            for name in ("kruskal", "prim_matrix", "prim_fibonacci"):
                if name == "kruskal":
                    (w, _, st), _, mem = measure(kruskal, V, E, mem=True)
                    _, dt, _ = measure(kruskal, V, E, instrument_sort=False)
                elif name == "prim_matrix":
                    M = build_matrix(V, E)  # building the matrix is part of the cost of that representation
                    (w, _, st), dt, mem = measure(prim_matrix, V, M, mem=True)
                    st = dict(st); st["ops"] += V * V  # matrix initialisation O(V^2)
                else:
                    (w, _, st), dt, mem = measure(prim_fibonacci, V, E, mem=True)
                ref = w if ref is None else ref
                assert w == ref, "MST weights disagree!"
                rows.append(row("mst", name, fam, V, st["ops"], dt, E=len(E), mst_weight=w, peak_kib=round(mem or 0, 1),
                                memory_units=st.get("memory_units"), decrease_keys=st.get("decrease_keys")))
    return rows, {}


# ------------------------------------------------------------------ knapsack
def suite_knapsack():
    rows, aux = [], {"knapsack_quality": [], "knapsack_capacity": []}
    for W in (1000, 2000, 4000, 8000, 16000, 32000):                      # capacity stress, n fixed
        items = G.knapsack_items(100, W, "random")
        (v1, _, st1), dt1, mem_roll = measure(knapsack_01, items, W, mem=True)
        _, _, mem_tab = measure(knapsack_01, items, W, keep_table=True, mem=True)
        (vf, stf), dtf, _ = measure(fractional_knapsack, items, W)
        rows.append(row("knapsack", "knapsack_01_dp", "capacity_stress(n=100)", W, st1["ops"], dt1, peak_kib_rolling=round(mem_roll, 1),
                        peak_kib_table=round(mem_tab, 1), value=v1))
        rows.append(row("knapsack", "fractional_knapsack", "capacity_stress(n=100)", W, stf["ops"], dtf, value=round(vf, 2)))
    for n in (50, 100, 200, 400, 800, 1600):                              # item-count stress, W fixed
        items = G.knapsack_items(n, 1000, "random")
        (v1, _, st1), dt1, _ = measure(knapsack_01, items, 1000)
        (vf, stf), dtf, _ = measure(fractional_knapsack, items, 1000)
        rows.append(row("knapsack", "knapsack_01_dp", "item_stress(W=1000)", n, st1["ops"], dt1, value=v1))
        rows.append(row("knapsack", "fractional_knapsack", "item_stress(W=1000)", n, stf["ops"], dtf, value=round(vf, 2)))
    for kind in ("random", "correlated", "ratio_trap"):                   # matched quality datasets
        for W in (100, 1000, 10000):
            items = G.knapsack_items(30, W, kind, seed=3)
            vf, _ = fractional_knapsack(items, W); v1, _, _ = knapsack_01(items, W); vg, _ = greedy_01(items, W)
            aux["knapsack_quality"].append(dict(dataset=kind, n=30, W=W, fractional=round(vf, 1), dp_01=v1, greedy_01=vg,
                                                greedy_gap_pct=round(100 * (v1 - vg) / v1, 1) if v1 else 0,
                                                frac_minus_01=round(vf - v1, 1)))
    # pseudo-polynomial demonstration: same items, W scaled by 10^k -> ops scale by 10^k
    items = [(v, w) for v, w in G.knapsack_items(40, 100, "random", seed=5)]
    for k in range(0, 5):
        W = 100 * 10 ** k
        (v, _, st), dt, _ = measure(knapsack_01, items, W)
        aux["knapsack_capacity"].append(dict(W=W, bits=W.bit_length(), dp_cell_updates=st["ops"], seconds=round(dt, 4)))
    return rows, aux


# ------------------------------------------------------------------------ dp
def suite_dp():
    rows, aux = [], {"mcm_order_benefit": []}
    for fam, dens in (("dense", 1.0), ("sparse(~3 out-edges)", 0.0)):
        for n in (20, 40, 60, 80, 100, 120, 140, 160):
            D = G.fw_matrix(n, dens if dens == 1.0 else 3 / n, seed=n)
            (d, st), dt, mem = measure(floyd_warshall, D, mem=(n in (40, 160)))
            rows.append(row("dp", "floyd_warshall", fam, n, st["ops"], dt, updates=st["updates"], memory_units=n * n,
                            peak_kib=round(mem, 1) if mem else None))
    for fam in ("random", "alternating"):
        for n in (10, 20, 40, 80, 120, 160, 200):
            p = G.mcm_dims(n, fam, seed=n)
            (c, par, st), dt, mem = measure(matrix_chain, p, mem=(n in (40, 200)))
            rows.append(row("dp", "matrix_chain", f"{fam}_dims", n, st["ops"], dt, optimal_cost=c, memory_units=2 * n * n,
                            peak_kib=round(mem, 1) if mem else None))
            if n in (10, 20, 40, 80, 160):
                naive = left_to_right_cost(p)
                aux["mcm_order_benefit"].append(dict(dims=fam, matrices=n, optimal_mults=c, left_to_right_mults=naive,
                                                     reduction_factor=round(naive / c, 2)))
    return rows, aux


# -------------------------------------------------------------------- search
def suite_search():
    rows = []
    # N-Queen
    for n in range(4, 13):
        (st, status), dt, _ = measure(n_queens, n, True)
        rows.append(row("search", "n_queens", "all_solutions", n, st["states"], dt, status, pruned=st["pruned"], solutions=st["solutions"]))
    for n in list(range(4, 25)):
        (st, status), dt, _ = measure(n_queens, n, False, 2_000_000)
        rows.append(row("search", "n_queens", "first_solution", n, st["states"], dt, status, pruned=st["pruned"]))
    # Hamiltonian cycle
    for kind in ("complete", "sparse_random", "clique_pendant"):
        for n in range(4, 13):
            adj = G.hamiltonian_graph(n, kind, seed=n)
            (st, status), dt, _ = measure(hamiltonian_cycle, adj)
            rows.append(row("search", "hamiltonian_backtracking", kind, n, st["states"], dt, status, pruned=st["pruned"], found=st["found"]))
    # TSP: three exact methods x three cost structures
    for kind in ("euclidean", "uniform", "flat"):
        for n in range(4, 12):
            D = G.tsp_matrix(n, kind, seed=n)
            (st, status), dt, _ = measure(tsp_backtracking, D, False)
            rows.append(row("search", "tsp_backtracking", kind, n, st["states"], dt, status, pruned=0, best=st["best"], memory_units=n))
        for n in range(4, 13):
            D = G.tsp_matrix(n, kind, seed=n)
            (st, status), dt, _ = measure(tsp_backtracking, D, True, 1_200_000)
            rows.append(row("search", "tsp_backtracking_pruned", kind, n, st["states"], dt, status, pruned=st["pruned"], best=st["best"], memory_units=n))
        for n in range(4, 15):
            D = G.tsp_matrix(n, kind, seed=n)
            (st, status), dt, _ = measure(tsp_branch_and_bound, D)
            rows.append(row("search", "tsp_branch_and_bound", kind, n, st["states"], dt, status, pruned=st["pruned"],
                            max_queue=st["max_queue"], expanded=st["expanded"], best=st["best"], memory_units=st["memory_units"]))
            if status != "ok" and n >= 13:
                break
    return rows, {}


SUITES = {"heaps": suite_heaps, "trees": suite_trees, "mst": suite_mst, "knapsack": suite_knapsack,
          "dp": suite_dp, "search": suite_search}

ALGO_TO_SUITE = {"binomial_heap": "heaps", "fibonacci_heap": "heaps", "b_tree": "trees", "red_black_tree": "trees",
                 "kruskal": "mst", "prim": "mst", "prim_matrix": "mst", "prim_fibonacci": "mst",
                 "fractional_knapsack": "knapsack", "knapsack_01": "knapsack", "knapsack_01_dp": "knapsack",
                 "floyd_warshall": "dp", "matrix_chain": "dp",
                 "hamiltonian": "search", "n_queens": "search", "tsp": "search", "tsp_backtracking": "search",
                 "tsp_branch_and_bound": "search"}
