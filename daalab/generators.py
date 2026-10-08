"""Test-family generators (all seeded -> reproducible)."""
import math
import random

INF = float("inf")


def connected_graph(n, m, seed, wmax=10_000):
    """Connected simple graph with n vertices and ~m edges. Returns [(w,u,v)]."""
    rnd = random.Random(seed)
    edges, seen = [], set()
    for v in range(1, n):
        u = rnd.randrange(v)
        seen.add((u, v)); edges.append((rnd.randint(1, wmax), u, v))
    maxm = n * (n - 1) // 2
    m = min(m, maxm)
    while len(edges) < m:
        u, v = rnd.sample(range(n), 2)
        if u > v:
            u, v = v, u
        if (u, v) not in seen:
            seen.add((u, v)); edges.append((rnd.randint(1, wmax), u, v))
    return edges


def sparse_graph(n, seed=1):
    return connected_graph(n, 2 * n, seed)


def dense_graph(n, seed=1):
    return connected_graph(n, int(0.8 * n * (n - 1) / 2), seed)


def prim_decrease_adversary(n):
    """Complete graph where each newly added vertex improves the key of EVERY
    remaining vertex -> ~E decrease-key calls (stress for Prim+heap)."""
    return [((n - i) * n + j, i, j) for i in range(n) for j in range(i + 1, n)]


def fw_matrix(n, density, seed=1, wmax=100):
    rnd = random.Random(seed)
    D = [[INF] * n for _ in range(n)]
    for i in range(n):
        D[i][i] = 0
        for j in range(n):
            if i != j and rnd.random() < density:
                D[i][j] = rnd.randint(1, wmax)
        D[i][(i + 1) % n] = min(D[i][(i + 1) % n], rnd.randint(1, wmax))  # keep strongly connected
    return D


def knapsack_items(n, W, kind, seed=1):
    rnd = random.Random(seed)
    wmax = max(2, W // 5)
    if kind == "random":
        return [(rnd.randint(1, wmax), rnd.randint(1, wmax)) for _ in range(n)]  # (value, weight)
    if kind == "correlated":
        ws = [rnd.randint(1, wmax) for _ in range(n)]
        return [(w + max(1, wmax // 10), w) for w in ws]
    if kind == "ratio_trap":
        # tiny very-dense item + one big item filling the sack: greedy-by-ratio loses
        items = [(2, 1), (W, W)]
        items += [(1, rnd.randint(2, wmax)) for _ in range(n - 2)]
        return items
    raise ValueError(kind)


def mcm_dims(n, kind, seed=1):
    rnd = random.Random(seed)
    if kind == "random":
        return [rnd.randint(5, 100) for _ in range(n + 1)]
    if kind == "alternating":  # big, small, big, small ... order matters hugely
        return [1000 if i % 2 == 0 else 10 for i in range(n + 1)]
    raise ValueError(kind)


def tsp_matrix(n, kind, seed=1):
    rnd = random.Random(seed)
    if kind == "euclidean":
        pts = [(rnd.randint(0, 100), rnd.randint(0, 100)) for _ in range(n)]
        return [[round(math.dist(a, b)) for b in pts] for a in pts]
    D = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            D[i][j] = D[j][i] = rnd.randint(1, 100) if kind == "uniform" else 100 + rnd.randint(0, 2)
    return D


def hamiltonian_graph(n, kind, seed=1):
    """Adjacency lists. kind: complete | sparse_random | clique_pendant (NO cycle)."""
    rnd = random.Random(seed)
    adj = [[] for _ in range(n)]

    def add(u, v):
        adj[u].append(v); adj[v].append(u)

    if kind == "complete":
        for u in range(n):
            for v in range(u + 1, n):
                add(u, v)
    elif kind == "sparse_random":
        for u in range(n):
            add(u, (u + 1) % n) if rnd.random() < 0.0 else None
        for u in range(n):
            for v in range(u + 1, n):
                if rnd.random() < 0.35:
                    add(u, v)
    elif kind == "clique_pendant":
        for u in range(n - 1):
            for v in range(u + 1, n - 1):
                add(u, v)
        add(n - 2, n - 1)  # vertex n-1 has degree 1 -> no Hamiltonian cycle
    else:
        raise ValueError(kind)
    return adj
