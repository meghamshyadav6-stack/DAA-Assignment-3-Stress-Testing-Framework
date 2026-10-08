"""Minimum spanning tree: Kruskal (sort + union-find), Prim with adjacency matrix
(O(V^2)) and Prim with Fibonacci heap (O(E + V log V))."""
from .ds_fibonacci import FibonacciHeap
from .util import counted_sorted

INF = float("inf")


class _DSU:
    def __init__(self, n):
        self.p = list(range(n))
        self.r = [0] * n
        self.steps = 0

    def find(self, x):
        root = x
        while self.p[root] != root:
            root = self.p[root]
            self.steps += 1
        while self.p[x] != root:
            self.p[x], x = root, self.p[x]
        self.steps += 1
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.r[ra] < self.r[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]:
            self.r[ra] += 1
        return True


def kruskal(n, edges, instrument_sort=True):
    """edges: list of (w,u,v). Returns (total_weight, mst_edges, stats). If the
    graph is disconnected the result is a minimum spanning forest."""
    if instrument_sort:
        es, sort_cmp = counted_sorted(edges, key=lambda e: e[0])
    else:
        es, sort_cmp = sorted(edges, key=lambda e: e[0]), 0
    dsu, total, tree = _DSU(n), 0, []
    for w, u, v in es:
        if dsu.union(u, v):
            total += w
            tree.append((w, u, v))
            if len(tree) == n - 1:
                break
    ops = sort_cmp + dsu.steps + len(edges)
    return total, tree, {"sort_comparisons": sort_cmp, "find_steps": dsu.steps, "ops": ops,
                         "memory_units": len(edges) + n}


def build_matrix(n, edges):
    M = [[INF] * n for _ in range(n)]
    for w, u, v in edges:
        M[u][v] = M[v][u] = w
    return M


def prim_matrix(n, M):
    """Classic O(V^2) Prim on an adjacency matrix."""
    if n == 0:
        return 0, [], {"ops": 0, "memory_units": 0}
    in_t, key, par = [False] * n, [INF] * n, [-1] * n
    key[0] = 0
    total, tree, ops = 0, [], 0
    for _ in range(n):
        u, best = -1, INF
        for v in range(n):
            ops += 1
            if not in_t[v] and (u == -1 or key[v] < best):
                u, best = v, key[v]
        if best == INF:
            break
        in_t[u] = True
        if par[u] != -1:
            total += best
            tree.append((best, par[u], u))
        row = M[u]
        for v in range(n):
            ops += 1
            if not in_t[v] and row[v] < key[v]:
                key[v], par[v] = row[v], u
    return total, tree, {"ops": ops, "memory_units": n * n + 3 * n}


def prim_fibonacci(n, edges):
    """Prim with a Fibonacci heap: V inserts, V extract-mins, <=E decrease-keys."""
    if n == 0:
        return 0, [], {"ops": 0, "memory_units": 0, "decrease_keys": 0}
    adj = [[] for _ in range(n)]
    for w, u, v in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    h = FibonacciHeap(track=True)
    key, par, in_t = [INF] * n, [-1] * n, [False] * n
    key[0] = 0
    for v in range(n):
        h.insert(key[v], v)
    total, tree, scans, dks = 0, [], 0, 0
    while len(h):
        kv, u = h.extract_min()
        if kv == INF:
            break
        in_t[u] = True
        if par[u] != -1:
            total += kv
            tree.append((kv, par[u], u))
        for v, w in adj[u]:
            scans += 1
            if not in_t[v] and w < key[v]:
                key[v], par[v] = w, u
                h.decrease_key(v, w)
                dks += 1
    return total, tree, {"ops": scans + h.work(), "heap_work": h.work(), "decrease_keys": dks,
                         "memory_units": n + 2 * len(edges) + 6 * n}
