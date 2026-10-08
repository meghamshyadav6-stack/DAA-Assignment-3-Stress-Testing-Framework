import time
import tracemalloc
from functools import cmp_to_key


class BudgetExceeded(Exception):
    """Raised when a search exceeds its state budget (used to flag 'High' risk)."""


def counted_sorted(seq, key, reverse=False):
    """sorted() that also returns the number of key comparisons performed."""
    cnt = 0

    def cmp(a, b):
        nonlocal cnt
        cnt += 1
        ka, kb = key(a), key(b)
        r = (ka > kb) - (ka < kb)
        return -r if reverse else r

    return sorted(seq, key=cmp_to_key(cmp)), cnt


def measure(fn, *args, mem=False, **kw):
    """Return (result, seconds, peak_kib_or_None). Memory uses a second traced run."""
    t0 = time.perf_counter()
    res = fn(*args, **kw)
    dt = time.perf_counter() - t0
    peak = None
    if mem:
        tracemalloc.start()
        fn(*args, **kw)
        _, p = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak = p / 1024.0
    return res, dt, peak
