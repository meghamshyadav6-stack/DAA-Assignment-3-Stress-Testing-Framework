"""Fibonacci heap (min-heap) with lazy insert/merge, consolidation on extract-min,
and cut / cascading-cut on decrease-key. All work is counted."""
from collections import defaultdict


class _FNode:
    __slots__ = ("key", "item", "degree", "parent", "child", "left", "right", "mark")

    def __init__(self, key, item):
        self.key, self.item = key, item
        self.degree = 0
        self.parent = self.child = None
        self.left = self.right = self
        self.mark = False


class FibonacciHeap:
    def __init__(self, track=False):
        self.min = None
        self.size = 0
        self.stats = defaultdict(int)
        self.handle = {} if track else None

    def __len__(self):
        return self.size

    def work(self):
        return sum(self.stats.values())

    # --- ring helpers -------------------------------------------------
    @staticmethod
    def _ring(x):
        out, cur = [x], x.right
        while cur is not x:
            out.append(cur)
            cur = cur.right
        return out

    def _add_root(self, x):
        x.parent = None
        if self.min is None:
            x.left = x.right = x
            self.min = x
        else:
            m = self.min
            x.left, x.right = m, m.right
            m.right.left = x
            m.right = x
        self.stats["root_list_ops"] += 1

    def insert(self, key, item=None):
        x = _FNode(key, item)
        if self.handle is not None:
            self.handle[item] = x
        self._add_root(x)
        self.stats["comparisons"] += 1
        if x.key < self.min.key:
            self.min = x
        self.size += 1

    def find_min(self):
        return self.min

    def merge(self, other):
        if other.min is None:
            return
        if self.min is None:
            self.min = other.min
        else:
            a, b = self.min, other.min
            ar, bl = a.right, b.left
            a.right, b.left = b, a
            bl.right, ar.left = ar, bl
            self.stats["comparisons"] += 1
            if b.key < a.key:
                self.min = b
        self.stats["root_list_ops"] += 1
        self.size += other.size
        if self.handle is not None and other.handle is not None:
            self.handle.update(other.handle)
        for k, v in other.stats.items():
            self.stats[k] += v
        other.min, other.size = None, 0

    def extract_min(self):
        z = self.min
        if z is None:
            raise IndexError("extract_min from empty heap")
        if z.child is not None:
            for c in self._ring(z.child):
                self.stats["root_list_ops"] += 1
                c.mark = False
                self._add_root(c)
            z.child = None
        if z.right is z:
            self.min = None
        else:
            z.left.right, z.right.left = z.right, z.left
            self.min = z.right
            self._consolidate()
        self.size -= 1
        if self.handle is not None:
            self.handle.pop(z.item, None)
        return z.key, z.item

    def _consolidate(self):
        roots = self._ring(self.min)
        table = {}
        for w in roots:
            self.stats["consolidate_steps"] += 1
            x, d = w, w.degree
            while d in table:
                y = table.pop(d)
                self.stats["comparisons"] += 1
                if y.key < x.key:
                    x, y = y, x
                y.parent = x
                y.mark = False
                if x.child is None:
                    y.left = y.right = y
                    x.child = y
                else:
                    c = x.child
                    y.left, y.right = c, c.right
                    c.right.left = y
                    c.right = y
                x.degree += 1
                self.stats["links"] += 1
                d += 1
            table[d] = x
        self.min = None
        for x in table.values():
            x.left = x.right = x
            self._add_root_keep(x)
        self.stats["consolidate_steps"] += len(table)

    def _add_root_keep(self, x):
        if self.min is None:
            self.min = x
        else:
            m = self.min
            x.left, x.right = m, m.right
            m.right.left = x
            m.right = x
            self.stats["comparisons"] += 1
            if x.key < self.min.key:
                self.min = x

    def _cut(self, x, y):
        if x.right is x:
            y.child = None
        else:
            x.left.right, x.right.left = x.right, x.left
            if y.child is x:
                y.child = x.right
        y.degree -= 1
        x.mark = False
        self.stats["cuts"] += 1
        self._add_root(x)

    def decrease_key(self, item, new_key):
        x = self.handle[item]
        if new_key > x.key:
            raise ValueError("new key larger than current key")
        x.key = new_key
        y = x.parent
        self.stats["comparisons"] += 1
        if y is not None and x.key < y.key:
            self._cut(x, y)
            while y.parent is not None:
                if not y.mark:
                    y.mark = True
                    break
                z = y.parent
                self._cut(y, z)
                self.stats["cascading_cuts"] += 1
                y = z
        self.stats["comparisons"] += 1
        if x.key < self.min.key:
            self.min = x
