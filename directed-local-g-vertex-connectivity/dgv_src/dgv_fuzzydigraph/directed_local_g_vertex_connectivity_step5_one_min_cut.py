"""Step 5 of Algorithm 6.1: one max-flow for t_yz and the extreme minimum cuts.

OneMinCut(F', F_yz, y, z), directed vertex-cut version:

  - weakest attachment M(v) = min{ xi(v -> u) : (v, u) arc of F' } for every
    internal vertex of the union graph - OUT-arcs only (a sink with no
    out-arc gets +infinity and can never enter a minimum cut); taking the
    in-arcs into account as well is a documented trap that changes weights;
  - minimum-cut network: every vertex v splits into v_in -> v_out with
    capacity M(v) (endpoints y, z get +infinity); every union arc u -> v is
    glued as the intermediate arc u_out -> v_in of capacity +infinity,
    KEEPING ITS DIRECTION (no bidirectionalization - that is the directed
    counterpart of the undirected edge version);
  - source y_out, sink z_in; one Dinic max-flow: the flow value is t_yz(F);
  - on the residual network, S_min collects the cut elements reachable from
    y_out and S_max those that cannot reach z_in (the two extreme minimum
    cuts in the sense of Picard-Queyranne).
No cut set is ever enumerated.
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


def weakest_attachment(skeleton, union, y, z):
    """M(v) = min{ xi(v -> u) : (v, u) arc of F' } - OUT-arcs only.

    Tabulated for every vertex of the skeleton except the endpoints (as in
    the chapter); a sink (no out-arc) gets +infinity and can never enter a
    minimum cut.  Only the internal vertices of the union graph enter the
    split network, the rest of the table is reported for reference.
    """
    M = {}
    for v in sorted(skeleton.vertices):
        if v == y or v == z:
            continue
        out = skeleton.out_adj.get(v, {})
        M[v] = min(out.values()) if out else INF_CAP
    return M


def one_min_cut(skeleton, union, y, z, M):
    """OneMinCut(F', F_yz, y, z): returns (t_yz, S_min, S_max)."""
    order = sorted(union.vertices)
    idx_in = {v: 2 * i for i, v in enumerate(order)}
    idx_out = {v: 2 * i + 1 for i, v in enumerate(order)}
    net = Dinic(2 * len(order))

    for v in order:
        if v == y or v == z:
            continue  # endpoints: no split arc (capacity +infinity)
        net.add_edge(idx_in[v], idx_out[v], M[v])
    for (u, v), _ in union.arcs.items():
        net.add_edge(idx_out[u], idx_in[v], INF_CAP)   # direction kept

    s, t = idx_out[y], idx_in[z]
    t_yz = net.max_flow(s, t)

    A = net.reachable_from(s)
    B = net.reachable_to(t)
    s_min = [v for v in order
             if v not in (y, z) and idx_in[v] in A and idx_out[v] not in A]
    s_max = [v for v in order
             if v not in (y, z) and idx_in[v] not in B and idx_out[v] in B]
    return t_yz, s_min, s_max
