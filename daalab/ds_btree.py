"""B-Tree of minimum degree t (CLRS). Insert uses proactive splitting. Counters:
key_comparisons, node_accesses (proxy for disk reads), splits."""
from collections import defaultdict


class _Node:
    __slots__ = ("keys", "children", "leaf")

    def __init__(self, leaf):
        self.keys, self.children, self.leaf = [], [], leaf


class BTree:
    def __init__(self, t=8):
        if t < 2:
            raise ValueError("minimum degree t must be >= 2")
        self.t = t
        self.root = _Node(True)
        self.node_count = 1
        self.height = 1
        self.n = 0
        self.stats = defaultdict(int)

    def search(self, k):
        node = self.root
        while True:
            self.stats["node_accesses"] += 1
            i = 0
            while i < len(node.keys):
                self.stats["key_comparisons"] += 1
                if k > node.keys[i]:
                    i += 1
                else:
                    break
            if i < len(node.keys) and node.keys[i] == k:
                return True
            if node.leaf:
                return False
            node = node.children[i]

    def _split_child(self, parent, i):
        t = self.t
        y = parent.children[i]
        z = _Node(y.leaf)
        mid = y.keys[t - 1]
        z.keys = y.keys[t:]
        y.keys = y.keys[: t - 1]
        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]
        parent.children.insert(i + 1, z)
        parent.keys.insert(i, mid)
        self.node_count += 1
        self.stats["splits"] += 1

    def insert(self, k):
        if self.search_quiet(k):
            return False
        r = self.root
        if len(r.keys) == 2 * self.t - 1:
            s = _Node(False)
            s.children.append(r)
            self.root = s
            self.node_count += 1
            self.height += 1
            self._split_child(s, 0)
            r = s
        self._insert_nonfull(r, k)
        self.n += 1
        return True

    def search_quiet(self, k):
        """duplicate check that does not pollute the counters"""
        saved = dict(self.stats)
        res = self.search(k)
        self.stats.clear()
        self.stats.update(saved)
        return res

    def _insert_nonfull(self, x, k):
        while True:
            self.stats["node_accesses"] += 1
            i = len(x.keys) - 1
            if x.leaf:
                while i >= 0 and k < x.keys[i]:
                    self.stats["key_comparisons"] += 1
                    i -= 1
                if i >= 0:
                    self.stats["key_comparisons"] += 1
                x.keys.insert(i + 1, k)
                return
            while i >= 0 and k < x.keys[i]:
                self.stats["key_comparisons"] += 1
                i -= 1
            if i >= 0:
                self.stats["key_comparisons"] += 1
            i += 1
            if len(x.children[i].keys) == 2 * self.t - 1:
                self._split_child(x, i)
                self.stats["key_comparisons"] += 1
                if k > x.keys[i]:
                    i += 1
            x = x.children[i]

    def work(self):
        return sum(self.stats.values())

    def utilization(self):
        return self.n / (self.node_count * (2 * self.t - 1))

    def check(self):
        """Validate B-tree invariants; returns True or raises AssertionError."""
        t = self.t
        depths = set()

        def rec(node, depth, lo, hi, is_root):
            assert node.keys == sorted(node.keys)
            assert all((lo is None or lo < k) and (hi is None or k < hi) for k in node.keys)
            assert len(node.keys) <= 2 * t - 1
            if not is_root:
                assert len(node.keys) >= t - 1
            if node.leaf:
                depths.add(depth)
                return
            assert len(node.children) == len(node.keys) + 1
            bounds = [lo] + node.keys + [hi]
            for i, c in enumerate(node.children):
                rec(c, depth + 1, bounds[i], bounds[i + 1], False)

        rec(self.root, 1, None, None, True)
        assert len(depths) == 1
        return True
