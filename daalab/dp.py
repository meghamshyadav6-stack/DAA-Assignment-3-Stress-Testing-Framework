"""Floyd-Warshall (all-pairs shortest paths) and Matrix Chain Multiplication."""
INF = float("inf")


def floyd_warshall(D):
    n = len(D)
    d = [row[:] for row in D]
    comps = updates = 0
    for k in range(n):
        dk = d[k]
        for i in range(n):
            di = d[i]
            dik = di[k]
            comps += n
            for j in range(n):
                nd = dik + dk[j]
                if nd < di[j]:
                    di[j] = nd
                    updates += 1
    neg_cycle = any(d[i][i] < 0 for i in range(n))
    return d, {"ops": comps, "updates": updates, "neg_cycle": neg_cycle, "memory_units": n * n}


def matrix_chain(p):
    """p has n+1 entries for n matrices (A_i is p[i] x p[i+1]).
    Returns (min_scalar_mults, parenthesization, stats)."""
    n = len(p) - 1
    if n <= 0:
        return 0, "", {"ops": 0}
    m = [[0] * n for _ in range(n)]
    s = [[0] * n for _ in range(n)]
    iters = 0
    for L in range(2, n + 1):
        for i in range(n - L + 1):
            j = i + L - 1
            best, bk = INF, -1
            pij = p[i]
            for k in range(i, j):
                iters += 1
                c = m[i][k] + m[k + 1][j] + pij * p[k + 1] * p[j + 1]
                if c < best:
                    best, bk = c, k
            m[i][j], s[i][j] = best, bk

    def paren(i, j):
        if i == j:
            return f"A{i + 1}"
        k = s[i][j]
        return "(" + paren(i, k) + paren(k + 1, j) + ")"

    return m[0][n - 1], paren(0, n - 1), {"ops": iters, "memory_units": 2 * n * n}


def left_to_right_cost(p):
    return sum(p[0] * p[k] * p[k + 1] for k in range(1, len(p) - 1))
