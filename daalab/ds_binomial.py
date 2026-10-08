"""Binomial heap (min-heap). Roots are kept in a dict degree -> tree, so union is
binary addition of two heaps. Every comparison / link / pointer step is counted."""
from collections import defaultdict


class _BNode:
    __slots__ = ("key", "item", "degree", "children", "parent")

    def __init__(self, key, item):
        self.key, self.item = key, item
        self.degree, self.children, self.parent = 0, [], None


class BinomialHeap:
    def __init__(self, track=False):
        self.roots = {}
        self.size = 0
        self.stats = defaultdict(int)
        self.handle = {} if track else None

    def __len__(self):
        return self.size

    def work(self):
        return sum(self.stats.values())

    def _link(self, a, b):
        self.stats["comparisons"] += 1
        if b.key < a.key:
            a, b = b, a
        b.parent = a
        a.children.append(b)
        a.degree += 1
        self.stats["links"] += 1
        return a

    def _union(self, other):
        new = dict(self.roots)
        carry = None
        top = max(other) if other else -1
        d = 0
        while d <= top or carry is not None:
            self.stats["degree_steps"] += 1
            ts = [t for t in (new.get(d), other.get(d), carry) if t is not None]
            carry = None
            new.pop(d, None)
            if len(ts) == 1:
                new[d] = ts[0]
            elif len(ts) == 2:
                carry = self._link(ts[0], ts[1])
            elif len(ts) == 3:
                new[d] = ts[0]
                carry = self._link(ts[1], ts[2])
            d += 1
        self.roots = new

    def insert(self, key, item=None):
        node = _BNode(key, item)
        if self.handle is not None:
            self.handle[item] = node
        self._union({0: node})
        self.size += 1

    def find_min(self):
        m = None
        for t in self.roots.values():
            self.stats["comparisons"] += 1
            if m is None or t.key < m.key:
                m = t
        return m

    def extract_min(self):
        m = self.find_min()
        if m is None:
            raise IndexError("extract_min from empty heap")
        del self.roots[m.degree]
        kids = {}
        for c in m.children:
            c.parent = None
            kids[c.degree] = c
        self._union(kids)
        self.size -= 1
        if self.handle is not None:
            self.handle.pop(m.item, None)
        return m.key, m.item

    def decrease_key(self, item, new_key):
        x = self.handle[item]
        if new_key > x.key:
            raise ValueError("new key larger than current key")
        x.key = new_key
        while x.parent is not None:
            self.stats["comparisons"] += 1
            p = x.parent
            if x.key < p.key:
                x.key, p.key = p.key, x.key
                x.item, p.item = p.item, x.item
                if self.handle is not None:
                    self.handle[x.item] = x
                    self.handle[p.item] = p
                self.stats["sift_swaps"] += 1
                x = p
            else:
                break

    def merge(self, other):
        self._union(other.roots)
        self.size += other.size
        if self.handle is not None and other.handle is not None:
            self.handle.update(other.handle)
        for k, v in other.stats.items():
            self.stats[k] += v
        other.roots, other.size = {}, 0
