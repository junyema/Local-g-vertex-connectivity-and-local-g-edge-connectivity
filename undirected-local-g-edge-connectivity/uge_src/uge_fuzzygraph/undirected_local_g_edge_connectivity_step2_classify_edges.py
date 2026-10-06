"""Step 2 of Algorithm 5.2: connectivity strength and edge bisection (ClassifyEdges).

Bisects the edge set into strong edges E_s(F) and non-strong edges E_n(F):
  E_s(F) = { e : xi(e) = conn_F(e) }   (strong)
  E_n(F) = { e : xi(e) < conn_F(e) }   (non-strong)

The structural criterion (Lemma: e is non-strong iff its two endpoints are
already connected in the subgraph made of edges with STRICTLY LARGER membership
value) is evaluated with a Kruskal-style scan: edges sorted by membership value
in descending order, grouped by equal value; inside a group every edge is first
classified (the union-find then only contains strictly heavier edges), and the
whole group is merged into the union-find afterwards.  O(m log m).

The edge-cut version has no special case at the end of Step 2: when y and z
are directly linked, the direct edge itself is the lightest (trivial) cut and
the max-flow of Step 5 simply returns xi(yz).
"""

EPS = 1e-9


class _UnionFind:
    def __init__(self, items):
        self.parent = {x: x for x in items}
        self.rank = {x: 0 for x in items}

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:          # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1

    def connected(self, a, b):
        return self.find(a) == self.find(b)


def classify_edges(F, eps=EPS):
    """ClassifyEdges(F): returns (strong, weak).

    strong / weak are lists of (u, v, xi) with u <= v; the two lists together
    exhaust the edge set (no third class exists).
    """
    ordered = sorted(F.edges.items(), key=lambda kv: kv[1], reverse=True)
    # Group edges with (numerically) equal membership values.
    groups = []
    for key, xi in ordered:
        if groups and abs(xi - groups[-1][0][1]) <= eps:
            groups[-1].append((key, xi))
        else:
            groups.append([(key, xi)])

    uf = _UnionFind(F.vertices)
    strong, weak = [], []
    for group in groups:
        # First classify: the union-find currently holds only heavier edges.
        for (u, v), xi in group:
            if uf.connected(u, v):
                weak.append((u, v, xi))
            else:
                strong.append((u, v, xi))
        # Then merge the whole group at once.
        for (u, v), _ in group:
            uf.union(u, v)
    return strong, weak
