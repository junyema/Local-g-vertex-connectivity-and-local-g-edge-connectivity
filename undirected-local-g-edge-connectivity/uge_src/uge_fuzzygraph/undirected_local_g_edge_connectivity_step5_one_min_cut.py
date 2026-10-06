"""Step 5 of Algorithm 5.2: one max-flow for t'_yz and the extreme minimum cuts.

OneMinCut(F', F_yz, y, z), edge-cut version - the only substantial difference
from the vertex-cut version is the network (no M(v), no node splitting):

  - every union edge {u, v} is replaced by two opposite arcs u -> v and
    v -> u, both with capacity xi(e) (the edge itself is the unit price
    m(e) = xi(e), written directly on the arcs);
  - source y, sink z;
  - one Dinic max-flow: the flow value is t'_yz(F);
  - on the residual network, S_min collects the edges whose arcs leave the
    set reachable from y, and S_max those whose arcs enter the set that can
    still reach z (the two extreme minimum edge cuts, Picard-Queyranne).
No edge cut is ever enumerated.
"""

INF_CAP = 1e11          # the doc's "big number" for +infinity
_FLOW_EPS = 1e-9        # residual capacity below this counts as zero


class Dinic:
    """Dinic max-flow on a small float-capacity network."""

    def __init__(self, n):
        self.n = n
        self.to = []        # head of each arc
        self.cap = []       # residual capacity of each arc
        self.graph = [[] for _ in range(n)]   # node -> list of arc indices

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

    # -- residual reachability (Picard-Queyranne extreme cuts) ----------------
    def reachable_from(self, s):
        """Nodes reachable from s along arcs with positive residual capacity."""
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
        """Nodes that can reach t along arcs with positive residual capacity
        (= nodes reachable from t on the reversed residual graph)."""
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

    S_min / S_max are lists of union edges (u, v, xi), u <= v: the two
    extreme minimum edge cuts read off the residual network.
    """
    order = sorted(union.vertices)
    idx = {v: i for i, v in enumerate(order)}
    net = Dinic(len(order))
    for (u, v), xi in union.edges.items():
        net.add_edge(idx[u], idx[v], xi)   # both directions, capacity xi(e)
        net.add_edge(idx[v], idx[u], xi)

    s, t = idx[y], idx[z]
    t_yz = net.max_flow(s, t)

    A = net.reachable_from(s)   # source side
    B = net.reachable_to(t)     # nodes that can still reach the sink
    s_min, s_max = [], []
    for (u, v), xi in union.edges.items():
        if (idx[u] in A) != (idx[v] in A):
            s_min.append((u, v, xi))           # crosses the source-side cut
        if (idx[u] in B) != (idx[v] in B):
            s_max.append((u, v, xi))           # crosses the sink-side cut
    return t_yz, sorted(s_min), sorted(s_max)
