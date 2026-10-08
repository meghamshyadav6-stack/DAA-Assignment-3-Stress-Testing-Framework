"""Correctness + boundary tests. Each test is tagged NORMAL / LARGE / BOUNDARY / DIFFICULT
in its docstring (used by the report's test-case table). Run: python -m unittest -v"""
import itertools, os, random, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from daalab.ds_binomial import BinomialHeap
from daalab.ds_fibonacci import FibonacciHeap
from daalab.ds_btree import BTree
from daalab.ds_rbtree import RBTree
from daalab.graphs import kruskal, prim_matrix, prim_fibonacci, build_matrix
from daalab.knapsack import fractional_knapsack, knapsack_01, greedy_01
from daalab.dp import floyd_warshall, matrix_chain, left_to_right_cost, INF
from daalab.search import n_queens, hamiltonian_cycle, tsp_backtracking, tsp_branch_and_bound
from daalab import generators as G


class TestHeaps(unittest.TestCase):
    def _sorted_out(self, H):
        rnd = random.Random(3); keys = rnd.sample(range(10_000), 500)
        h = H(track=True)
        for i, k in enumerate(keys): h.insert(k, i)
        out = [h.extract_min()[0] for _ in range(len(keys))]
        self.assertEqual(out, sorted(keys))

    def test_normal_extract_sorted(self):
        """NORMAL"""
        self._sorted_out(BinomialHeap); self._sorted_out(FibonacciHeap)

    def test_decrease_key_and_merge(self):
        """NORMAL"""
        for H in (BinomialHeap, FibonacciHeap):
            a, b = H(track=True), H(track=True)
            for i in range(100): a.insert(1000 + i, i)
            for i in range(100, 200): b.insert(1000 + i, i)
            a.extract_min()  # force tree structure
            a.merge(b)
            a.decrease_key(150, -5); a.decrease_key(50, -9)
            self.assertEqual(a.extract_min(), (-9, 50)); self.assertEqual(a.extract_min(), (-5, 150))
            self.assertEqual(len(a), 197)

    def test_boundary_empty_and_single(self):
        """BOUNDARY"""
        for H in (BinomialHeap, FibonacciHeap):
            h = H()
            with self.assertRaises(IndexError): h.extract_min()
            h.insert(7, "x"); self.assertEqual(h.extract_min(), (7, "x")); self.assertEqual(len(h), 0)

    def test_difficult_decrease_storm_vs_reference(self):
        """DIFFICULT"""
        rnd = random.Random(5)
        for H in (BinomialHeap, FibonacciHeap):
            h = H(track=True); ref = {}
            for i in range(300):
                k = rnd.randint(1000, 9000); h.insert(k, i); ref[i] = k
            k, i = h.extract_min(); del ref[i]
            for step in range(250):
                it = rnd.choice(list(ref)); nk = ref[it] - rnd.randint(0, 500)
                h.decrease_key(it, nk); ref[it] = nk
                if step % 40 == 0:
                    k, i = h.extract_min(); self.assertEqual(k, min(list(ref.values()) + [k])); del ref[i]
            out = [h.extract_min()[0] for _ in range(len(h))]
            self.assertEqual(out, sorted(ref.values()))


class TestTrees(unittest.TestCase):
    def test_normal_and_large(self):
        """NORMAL / LARGE"""
        rnd = random.Random(1)
        for order in ("asc", "desc", "rand"):
            keys = list(range(20000)); 
            if order == "desc": keys.reverse()
            if order == "rand": rnd.shuffle(keys)
            bt, rb = BTree(t=4), RBTree()
            for k in keys: bt.insert(k); rb.insert(k)
            bt.check(); rb.check()
            self.assertTrue(all(bt.search(k) and rb.search(k) for k in rnd.sample(keys, 500)))
            self.assertFalse(bt.search(-1) or rb.search(-1))
            import math
            self.assertLessEqual(rb.height(), 2 * math.log2(rb.n + 1))  # RB height guarantee

    def test_boundary(self):
        """BOUNDARY"""
        bt, rb = BTree(t=2), RBTree()
        self.assertFalse(bt.search(1)); self.assertFalse(rb.search(1))
        bt.insert(1); rb.insert(1)
        self.assertFalse(bt.insert(1)); self.assertFalse(rb.insert(1))
        with self.assertRaises(ValueError): BTree(t=1)


class TestGraphs(unittest.TestCase):
    def test_mst_agree(self):
        """NORMAL / DIFFICULT (dense + decrease-key adversary + equal weights)"""
        cases = [(60, G.sparse_graph(60)), (40, G.dense_graph(40)), (30, G.prim_decrease_adversary(30)),
                 (20, [(5, u, v) for u in range(20) for v in range(u + 1, 20)])]
        for n, e in cases:
            wk, tk, _ = kruskal(n, e); wp, tp, _ = prim_matrix(n, build_matrix(n, e)); wf, tf, _ = prim_fibonacci(n, e)
            self.assertEqual(wk, wp); self.assertEqual(wk, wf)
            self.assertEqual(len(tk), n - 1); self.assertEqual(len(tp), n - 1); self.assertEqual(len(tf), n - 1)

    def test_boundary(self):
        """BOUNDARY"""
        self.assertEqual(kruskal(1, [])[0], 0); self.assertEqual(prim_matrix(1, [[INF]])[0], 0)
        self.assertEqual(prim_fibonacci(1, [])[0], 0)
        self.assertEqual(kruskal(2, [(4, 0, 1)])[0], 4)


class TestKnapsack(unittest.TestCase):
    def test_dp_matches_bruteforce(self):
        """NORMAL"""
        rnd = random.Random(2)
        for _ in range(40):
            items = [(rnd.randint(1, 30), rnd.randint(1, 15)) for _ in range(10)]; W = rnd.randint(1, 60)
            best = max(sum(items[i][0] for i in s) for r in range(11) for s in itertools.combinations(range(10), r)
                       if sum(items[i][1] for i in s) <= W)
            v, chosen, _ = knapsack_01(items, W, keep_table=True)
            self.assertEqual(v, best); self.assertEqual(sum(items[i][0] for i in chosen), best)
            self.assertLessEqual(sum(items[i][1] for i in chosen), W)
            self.assertLessEqual(v, fractional_knapsack(items, W)[0] + 1e-9)

    def test_greedy_fails_01_but_fractional_is_optimal(self):
        """DIFFICULT"""
        items, W = [(60, 10), (100, 20), (120, 30)], 50
        self.assertEqual(knapsack_01(items, W)[0], 220); self.assertEqual(greedy_01(items, W)[0], 160)
        self.assertAlmostEqual(fractional_knapsack(items, W)[0], 240.0)
        trap = G.knapsack_items(20, 1000, "ratio_trap")
        self.assertEqual(knapsack_01(trap, 1000)[0], 1000); self.assertLess(greedy_01(trap, 1000)[0], 50)

    def test_boundary(self):
        """BOUNDARY"""
        self.assertEqual(knapsack_01([(5, 3)], 0)[0], 0); self.assertEqual(knapsack_01([], 10)[0], 0)
        self.assertEqual(knapsack_01([(5, 30)], 10)[0], 0)
        self.assertAlmostEqual(fractional_knapsack([(30, 30)], 10)[0], 10.0)
        self.assertEqual(fractional_knapsack([], 10)[0], 0)


class TestDP(unittest.TestCase):
    def test_floyd_vs_bellman_ford(self):
        """NORMAL / LARGE"""
        n = 40; D = G.fw_matrix(n, 0.2, seed=4); d, _ = floyd_warshall(D)[0], None
        for s in (0, 7, 33):
            dist = [INF] * n; dist[s] = 0
            for _ in range(n):
                for u in range(n):
                    for v in range(n):
                        if dist[u] + D[u][v] < dist[v]: dist[v] = dist[u] + D[u][v]
            self.assertEqual(dist, d[s])

    def test_floyd_negative_cycle_and_boundary(self):
        """BOUNDARY / DIFFICULT"""
        self.assertTrue(floyd_warshall([[0, 1], [-3, 0]])[1]["neg_cycle"])
        self.assertEqual(floyd_warshall([[0]])[0], [[0]]); self.assertEqual(floyd_warshall([])[0], [])

    def test_mcm(self):
        """NORMAL / BOUNDARY"""
        c, s, _ = matrix_chain([10, 30, 5, 60]); self.assertEqual(c, 4500); self.assertEqual(s, "((A1A2)A3)")
        self.assertEqual(matrix_chain([5, 7])[0], 0); self.assertEqual(matrix_chain([5])[0], 0)
        c, _, _ = matrix_chain(G.mcm_dims(60, "alternating"))
        self.assertLess(c * 5, left_to_right_cost(G.mcm_dims(60, "alternating")))

    def test_mcm_vs_recursion(self):
        """NORMAL"""
        from functools import lru_cache
        p = G.mcm_dims(9, "random", seed=8)
        @lru_cache(None)
        def f(i, j): return 0 if i == j else min(f(i, k) + f(k + 1, j) + p[i] * p[k + 1] * p[j + 1] for k in range(i, j))
        self.assertEqual(matrix_chain(p)[0], f(0, 8))


class TestSearch(unittest.TestCase):
    def test_nqueens_counts(self):
        """NORMAL / BOUNDARY"""
        known = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92, 9: 352}
        for n, c in known.items(): self.assertEqual(n_queens(n)[0]["solutions"], c)
        st, _ = n_queens(8, find_all=False); self.assertEqual(st["solutions"], 1)
        pos = st["first"]; self.assertTrue(all(abs(pos[i] - pos[j]) != j - i and pos[i] != pos[j]
                                              for i in range(8) for j in range(i + 1, 8)))

    def test_hamiltonian(self):
        """NORMAL / DIFFICULT / BOUNDARY"""
        self.assertTrue(hamiltonian_cycle(G.hamiltonian_graph(8, "complete"))[0]["found"])
        self.assertFalse(hamiltonian_cycle(G.hamiltonian_graph(8, "clique_pendant"))[0]["found"])
        self.assertFalse(hamiltonian_cycle([[1], [0]])[0]["found"])   # n=2
        self.assertFalse(hamiltonian_cycle([[]])[0]["found"])         # n=1
        st, _ = hamiltonian_cycle(G.hamiltonian_graph(9, "sparse_random", seed=3))
        if st["found"]:
            adj = G.hamiltonian_graph(9, "sparse_random", seed=3); cyc = st["cycle"]
            self.assertEqual(sorted(cyc), list(range(9)))
            self.assertTrue(all(cyc[(i + 1) % 9] in adj[cyc[i]] for i in range(9)))

    def test_tsp_all_methods_agree(self):
        """NORMAL / DIFFICULT"""
        for kind in ("euclidean", "uniform", "flat"):
            for n in (1, 2, 3, 6, 8):
                D = G.tsp_matrix(n, kind, seed=n)
                brute = min((sum(D[a][b] for a, b in zip((0,) + p, p + (0,))) for p in itertools.permutations(range(1, n))), default=0)
                self.assertEqual(tsp_backtracking(D)[0]["best"], brute)
                self.assertEqual(tsp_backtracking(D, prune=True)[0]["best"], brute)
                self.assertEqual(tsp_branch_and_bound(D)[0]["best"], brute)

    def test_budget_flag(self):
        """DIFFICULT"""
        st, status = tsp_backtracking(G.tsp_matrix(11, "uniform"), budget=1000)
        self.assertEqual(status, "budget_exceeded")


if __name__ == "__main__":
    unittest.main(verbosity=2)
