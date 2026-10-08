"""Red-Black tree (CLRS) with insert + search. Counters: comparisons, rotations,
recolorings. check() validates all five RB properties."""
from collections import defaultdict

RED, BLACK = True, False


class _N:
    __slots__ = ("key", "color", "left", "right", "parent")

    def __init__(self, key=None, color=BLACK):
        self.key, self.color = key, color
        self.left = self.right = self.parent = None


class RBTree:
    def __init__(self):
        self.nil = _N()
        self.nil.left = self.nil.right = self.nil.parent = self.nil
        self.root = self.nil
        self.n = 0
        self.stats = defaultdict(int)

    def work(self):
        return sum(self.stats.values())

    def search(self, k):
        x = self.root
        while x is not self.nil:
            self.stats["comparisons"] += 1
            if k == x.key:
                return True
            x = x.left if k < x.key else x.right
        return False

    def _rot_left(self, x):
        y = x.right
        x.right = y.left
        if y.left is not self.nil:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is self.nil:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left, x.parent = x, y
        self.stats["rotations"] += 1

    def _rot_right(self, x):
        y = x.left
        x.left = y.right
        if y.right is not self.nil:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is self.nil:
            self.root = y
        elif x is x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right, x.parent = x, y
        self.stats["rotations"] += 1

    def insert(self, k):
        y, x = self.nil, self.root
        while x is not self.nil:
            y = x
            self.stats["comparisons"] += 1
            if k == x.key:
                return False
            x = x.left if k < x.key else x.right
        z = _N(k, RED)
        z.left = z.right = self.nil
        z.parent = y
        if y is self.nil:
            self.root = z
        elif k < y.key:
            y.left = z
        else:
            y.right = z
        self._fixup(z)
        self.n += 1
        return True

    def _fixup(self, z):
        while z.parent.color == RED:
            p, g = z.parent, z.parent.parent
            if p is g.left:
                u = g.right
                if u.color == RED:
                    p.color = u.color = BLACK
                    g.color = RED
                    self.stats["recolorings"] += 3
                    z = g
                else:
                    if z is p.right:
                        z = p
                        self._rot_left(z)
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self.stats["recolorings"] += 2
                    self._rot_right(z.parent.parent)
            else:
                u = g.left
                if u.color == RED:
                    p.color = u.color = BLACK
                    g.color = RED
                    self.stats["recolorings"] += 3
                    z = g
                else:
                    if z is p.left:
                        z = p
                        self._rot_right(z)
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self.stats["recolorings"] += 2
                    self._rot_left(z.parent.parent)
        if self.root.color == RED:
            self.root.color = BLACK
            self.stats["recolorings"] += 1

    def height(self):
        def h(x):
            return 0 if x is self.nil else 1 + max(h(x.left), h(x.right))
        return h(self.root)

    def check(self):
        assert self.root.color == BLACK
        def rec(x, lo, hi):
            if x is self.nil:
                return 1
            assert (lo is None or x.key > lo) and (hi is None or x.key < hi)
            if x.color == RED:
                assert x.left.color == BLACK and x.right.color == BLACK
            a, b = rec(x.left, lo, x.key), rec(x.right, x.key, hi)
            assert a == b
            return a + (1 if x.color == BLACK else 0)
        rec(self.root, None, None)
        return True
