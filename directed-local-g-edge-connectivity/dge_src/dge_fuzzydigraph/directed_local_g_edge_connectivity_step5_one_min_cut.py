"""Step 5 of Algorithm 6.2: one max-flow for t'_yz and the extreme minimum cuts.

OneMinCut(F_yz, y, z), directed arc-cut version:

  - every union arc u -> v becomes a network arc with capacity xi(e),
    direction KEPT (no bidirectionalization, no node splitting, no M(v) -
    the arc itself is its unit price m(e) = xi(e), written on the arc);
  - source y, sink z; one Dinic max-flow: the flow value is t'_yz(F);
  - on the residual network, S_min collects the arcs that leave the set
    reachable from y, and S_max those that enter the set that can still
    reach z (the two extreme minimum arc cuts, Picard-Queyranne).
No arc cut is ever enumerated.
"""

INF_CAP = 1e11          # the doc's "big number" for +infinity
_FLOW_EPS = 1e-9        # residual capacity below this counts as zero


class Dinic:
    """Dinic max-flow on a small float-capacity network."""

    def __init__(self, n):
        self.n = n
        self.to = []
        self.cap = []
        self.graph = [[] for _ in range(n)]

    def add_edge(self, u, v, capacity):
        self.graph[u].append(len(self.to))
        self.to.append(v)
        self.cap.append(capacity)
        self.graph[v].append(len(self.to))
        self.to.append(u)
        self.cap.append(0.0)

    def max_flow(self, s, t):
        flow = 0.0
        while True:
            level = [-1] * self.n
            level[s] = 0
            queue = [s]
            while queue:
                nxt = []
                for u in queue:
                    for a in self.graph[u]:
                        v = self.to[a]
                        if self.cap[a] > _FLOW_EPS and level[v] < 0:
                            level[v] = level[u] + 1
                            nxt.append(v)
                queue = nxt
            if level[t] < 0:
                return flow
            it = [0] * self.n

            def dfs(u, limit):
                if u == t:
                    return limit
                while it[u] < len(self.graph[u]):
                    a = self.graph[u][it[u]]
                    v = self.to[a]
                    if self.cap[a] > _FLOW_EPS and level[v] == level[u] + 1:
                        got = dfs(v, min(limit, self.cap[a]))
                        if got > _FLOW_EPS:
                            self.cap[a] -= got
                            self.cap[a ^ 1] += got
                            return got
                    it[u] += 1
                return 0.0

            while True:
                pushed = dfs(s, INF_CAP)
                if pushed <= _FLOW_EPS:
                    break
                flow += pushed

    def reachable_from(self, s):
        seen = {s}
        queue = [s]
        while queue:
            nxt = []
            for u in queue:
                for a in self.graph[u]:
                    v = self.to[a]
                    if self.cap[a] > _FLOW_EPS and v not in seen:
                        seen.add(v)
                        nxt.append(v)
            queue = nxt
        return seen

    def reachable_to(self, t):
        rev = [[] for _ in range(self.n)]
        for u in range(self.n):
            for a in self.graph[u]:
                if self.cap[a] > _FLOW_EPS:
                    rev[self.to[a]].append(u)
        seen = {t}
        queue = [t]
        while queue:
            nxt = []
            for u in queue:
                for v in rev[u]:
                    if v not in seen:
                        seen.add(v)
                        nxt.append(v)
            queue = nxt
        return seen


def one_min_cut(union, y, z):
    """OneMinCut(F_yz, y, z): returns (t'_yz, S_min, S_max).

    S_min / S_max are lists of union arcs (u, v, xi): the two extreme minimum
    arc cuts read off the residual network.
    """
    order = sorted(union.vertices)
    idx = {v: i for i, v in enumerate(order)}
    net = Dinic(len(order))
    for (u, v), xi in union.arcs.items():
        net.add_edge(idx[u], idx[v], xi)   # direction kept, capacity xi(e)

    s, t = idx[y], idx[z]
    t_yz = net.max_flow(s, t)

    A = net.reachable_from(s)   # source side
    B = net.reachable_to(t)     # nodes that can still reach the sink
    s_min, s_max = [], []
    for (u, v), xi in union.arcs.items():
        if idx[u] in A and idx[v] not in A:
            s_min.append((u, v, xi))           # leaves the source side
        if idx[u] not in B and idx[v] in B:
            s_max.append((u, v, xi))           # enters the sink side
    return t_yz, sorted(s_min), sorted(s_max)
