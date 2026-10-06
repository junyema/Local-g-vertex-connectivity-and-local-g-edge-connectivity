"""Step 5 of Algorithm 5.1: one max-flow for t_yz and the extreme minimum cuts.

OneMinCut(F', F_yz, y, z):
  - weakest attachment M(v) = min{ xi(v, u) : (v, u) in E(F') } for every
    internal vertex of the union graph (isolated vertices get +infinity);
  - minimum-cut network: every vertex v splits into v_in -> v_out with
    capacity M(v) (endpoints y, z get +infinity); every union edge {u, v}
    becomes two opposite arcs u_out -> v_in and v_out -> u_in of capacity
    +infinity; source y_out, sink z_in;
  - one Dinic max-flow: the flow value is t_yz(F);
  - on the residual network, S_min collects the cut elements reachable from
    y_out and S_max those that cannot reach z_in (the two extreme minimum cuts
    in the sense of Picard-Queyranne).
No cut set is ever enumerated.
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


def weakest_attachment(skeleton, union, y, z):
    """M(v) = min{ xi(v, u) : (v, u) in E(F') } for v in V(F') \\ {y, z}.

    The minimum is taken over the SKELETON (hanging leaves and detour
    vertices count, as tabulated in the chapter); a vertex with no incident
    edge in F' gets +infinity.  Only the internal vertices of the union graph
    enter the split network, the rest of the table is reported for reference.
    """
    M = {}
    for v in sorted(skeleton.vertices):
        if v == y or v == z:
            continue
        inc = skeleton.adj.get(v, {})
        M[v] = min(inc.values()) if inc else INF_CAP
    return M


def one_min_cut(skeleton, union, y, z, M):
    """OneMinCut(F', F_yz, y, z): returns (t_yz, S_min, S_max).

    S_min / S_max are the two extreme minimum vertex cuts, read off the
    residual network (lists of internal union-graph vertices, sorted).
    """
    order = sorted(union.vertices)
    idx_in = {v: 2 * i for i, v in enumerate(order)}
    idx_out = {v: 2 * i + 1 for i, v in enumerate(order)}
    net = Dinic(2 * len(order))

    for v in order:
        if v == y or v == z:
            continue  # endpoints: no split arc (capacity +infinity)
        net.add_edge(idx_in[v], idx_out[v], M[v])
    for (u, v), _ in union.edges.items():
        net.add_edge(idx_out[u], idx_in[v], INF_CAP)
        net.add_edge(idx_out[v], idx_in[u], INF_CAP)

    s, t = idx_out[y], idx_in[z]
    t_yz = net.max_flow(s, t)

    A = net.reachable_from(s)   # source side
    B = net.reachable_to(t)     # nodes that can still reach the sink
    s_min = [v for v in order
             if v not in (y, z) and idx_in[v] in A and idx_out[v] not in A]
    s_max = [v for v in order
             if v not in (y, z) and idx_in[v] not in B and idx_out[v] in B]
    return t_yz, s_min, s_max
