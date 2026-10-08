"""Backtracking / Branch-and-Bound: N-Queen, Hamiltonian cycle, TSP (pure
backtracking, pruned backtracking, best-first branch and bound)."""
from .ds_binomial import BinomialHeap
from .util import BudgetExceeded

INF = float("inf")


def n_queens(n, find_all=True, budget=5_000_000):
    """states = recursive calls (partial placements), pruned = rejected squares."""
    cols, d1, d2 = set(), set(), set()
    st = {"states": 0, "pruned": 0, "solutions": 0, "first": None}
    pos = []

    def rec(r):
        st["states"] += 1
        if st["states"] > budget:
            raise BudgetExceeded
        if r == n:
            st["solutions"] += 1
            if st["first"] is None:
                st["first"] = list(pos)
            return not find_all
        for c in range(n):
            if c in cols or (r - c) in d1 or (r + c) in d2:
                st["pruned"] += 1
                continue
            cols.add(c); d1.add(r - c); d2.add(r + c); pos.append(c)
            stop = rec(r + 1)
            cols.discard(c); d1.discard(r - c); d2.discard(r + c); pos.pop()
            if stop:
                return True
        return False

    status = "ok"
    try:
        rec(0)
    except BudgetExceeded:
        status = "budget_exceeded"
    st["max_depth_memory"] = n
    return st, status


def hamiltonian_cycle(adj, budget=1_500_000):
    """Decision problem: does a Hamiltonian cycle exist? (n < 3 -> False.)"""
    n = len(adj)
    st = {"states": 0, "pruned": 0, "found": False, "cycle": None}
    if n < 3:
        return st, "ok"
    nbr = [set(a) for a in adj]
    visited = [False] * n
    visited[0] = True
    path = [0]

    def rec(u, depth):
        st["states"] += 1
        if st["states"] > budget:
            raise BudgetExceeded
        if depth == n:
            if 0 in nbr[u]:
                st["found"], st["cycle"] = True, list(path)
                return True
            st["pruned"] += 1
            return False
        for v in adj[u]:
            if visited[v]:
                st["pruned"] += 1
                continue
            visited[v] = True; path.append(v)
            if rec(v, depth + 1):
                return True
            visited[v] = False; path.pop()
        return False

    status = "ok"
    try:
        rec(0, 1)
    except BudgetExceeded:
        status = "budget_exceeded"
    return st, status


def tsp_backtracking(D, prune=False, budget=1_200_000):
    """Exact TSP by DFS over permutations. prune=True cuts when partial cost >= best."""
    n = len(D)
    st = {"states": 0, "pruned": 0, "complete": 0, "best": INF, "tour": None}
    visited = [False] * n
    visited[0] = True
    path = [0]

    def rec(last, cost, depth):
        st["states"] += 1
        if st["states"] > budget:
            raise BudgetExceeded
        if depth == n:
            st["complete"] += 1
            total = cost + D[last][0]
            if total < st["best"]:
                st["best"], st["tour"] = total, list(path)
            return
        for v in range(n):
            if not visited[v]:
                nc = cost + D[last][v]
                if prune and nc >= st["best"]:
                    st["pruned"] += 1
                    continue
                visited[v] = True; path.append(v)
                rec(v, nc, depth + 1)
                visited[v] = False; path.pop()

    status = "ok"
    try:
        rec(0, 0, 1)
    except BudgetExceeded:
        status = "budget_exceeded"
    st["memory_units"] = n
    return st, status


def _nearest_neighbour(D):
    n = len(D)
    tour, seen, cost = [0], {0}, 0
    while len(tour) < n:
        u = tour[-1]
        v = min((x for x in range(n) if x not in seen), key=lambda x: D[u][x])
        cost += D[u][v]; tour.append(v); seen.add(v)
    return cost + D[tour[-1]][0], tour


def tsp_branch_and_bound(D, budget=60_000):
    """Best-first branch and bound. Live nodes sit in OUR Binomial Heap.
    Lower bound = cost so far + for every city that still has to be left
    (current city + unvisited) the cheapest edge into {unvisited} U {start}."""
    n = len(D)
    st = {"states": 0, "pruned": 0, "complete": 0, "expanded": 0, "max_queue": 0, "best": INF, "tour": None}
    if n == 1:
        st.update(best=0, tour=[0])
        return st, "ok"
    st["best"], st["tour"] = _nearest_neighbour(D)

    def bound(cost, last, rem):
        targets = rem | {0}
        lb = cost
        for u in (last, *rem):
            lb += min(D[u][v] for v in targets if v != u)
        return lb

    heap, uid = BinomialHeap(), 0
    rem0 = frozenset(range(1, n))
    heap.insert((bound(0, 0, rem0), 0, uid), (0, 0, rem0, (0,)))
    status = "ok"
    while len(heap):
        (lb, _, _), (cost, last, rem, path) = heap.extract_min()
        if lb >= st["best"]:
            st["pruned"] += 1 + len(heap)
            break
        st["expanded"] += 1
        for v in rem:
            st["states"] += 1
            if st["states"] > budget:
                status = "budget_exceeded"
                break
            nc = cost + D[last][v]
            nrem = rem - {v}
            if not nrem:
                st["complete"] += 1
                total = nc + D[v][0]
                if total < st["best"]:
                    st["best"], st["tour"] = total, list(path) + [v]
                continue
            nlb = bound(nc, v, nrem)
            if nlb >= st["best"]:
                st["pruned"] += 1
            else:
                uid += 1
                heap.insert((nlb, -(n - len(nrem)), uid), (nc, v, nrem, path + (v,)))
        st["max_queue"] = max(st["max_queue"], len(heap))
        if status != "ok":
            break
    st["memory_units"] = st["max_queue"] * n
    return st, status
