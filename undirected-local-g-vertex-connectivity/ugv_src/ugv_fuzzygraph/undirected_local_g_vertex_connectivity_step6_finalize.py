"""Step 6 of Algorithm 5.1: the two routes for D and the summary (Finalize).

D = max_{S in C*} d_{F'-S}(y, z)  (+infinity when C* contains a fatal cut).

Route 1 (extreme minimum cuts + two BFS): delete S_min, then S_max, from the
skeleton, measure d_{F'-S}(y, z) by BFS, take the larger value -> D1.

Route 2 (length-cap bisection): tau(L) is the least weight of a cut, taken on
union-graph vertices only, that severs every y-z walk of length <= L.  An edge
belongs to H_L iff min{d_y(u)+1+d_z(v), d_y(v)+1+d_z(u)} <= L; in the H_L
network the cut elements are the union-graph vertices only (their split arcs
keep the capacity M(v)); every structure element outside the union graph gets
a +infinity sentinel and cannot be cut.  tau is non-decreasing, tau(D) = t_yz,
so {L : tau(L) = t_yz} is a prefix [D, L*]; bisecting on [d, n-1] with
O(log n) min-cuts yields L*, and D2 = L* + 1 (D2 = +infinity when tau(n-1) is
still t_yz, the signature of a fatal cut).  Route 2 is only a lower bound on D
in general; both routes are provable lower bounds and the algorithm takes the
larger one.

Summary: D = max(D1, D2); if D = +infinity then
gamma_yz = (t_yz, 1), else gamma_yz = (t_yz, 1 - d_F(y,z)/D).
"""

import math

from .undirected_local_g_vertex_connectivity_step1_load_graph import FuzzyGraph
from .undirected_local_g_vertex_connectivity_step4_union_graph import bfs_distances

INF = math.inf
EPS = 1e-9


def _d_after_vertex_removal(skeleton, removed, y, z):
    """BFS on F' - S (S a vertex set): the y-z hop distance, or +infinity."""
    work = skeleton.copy()
    for v in removed:
        work.remove_vertex(v)
    dist = bfs_distances(work, y)
    return dist.get(z, INF)


def route_one(skeleton, s_min, s_max, y, z):
    """Route 1: delete the extreme minimum cuts, BFS twice, take the larger.

    Returns (D1, (d_min, d_max)) where d_min / d_max are the two distances.
    """
    d_min = _d_after_vertex_removal(skeleton, s_min, y, z)
    d_max = _d_after_vertex_removal(skeleton, s_max, y, z)
    d1 = max(d_min, d_max)
    return d1, (d_min, d_max)


def _tau(L, skeleton, d_y, d_z, union, M, y, z):
    """tau(L): one minimum cut on H_L whose cut elements are the union-graph
    vertices only (everything else carries the +infinity sentinel)."""
    # H_L: edge on it iff min{d_y(u)+1+d_z(v), d_y(v)+1+d_z(u)} <= L.
    h_edges = []
    for (u, v), xi in skeleton.edges.items():
        du = d_y.get(u, INF)
        dv = d_y.get(v, INF)
        zu = d_z.get(u, INF)
        zv = d_z.get(v, INF)
        if min(du + 1 + zv, dv + 1 + zu) <= L:
            h_edges.append((u, v))

    vertices = set(union.vertices)
    for u, v in h_edges:
        vertices.add(u)
        vertices.add(v)
    order = sorted(vertices)
    idx_in = {v: 2 * i for i, v in enumerate(order)}
    idx_out = {v: 2 * i + 1 for i, v in enumerate(order)}

    # Local Dinic (kept small; mirrors the network of Step 5).
    from .undirected_local_g_vertex_connectivity_step5_one_min_cut import Dinic, INF_CAP
    net = Dinic(2 * len(order))
    internal = set(union.vertices) - {y, z}
    for v in order:
        cap = M[v] if v in internal else INF_CAP
        net.add_edge(idx_in[v], idx_out[v], cap)
    for u, v in h_edges:
        net.add_edge(idx_out[u], idx_in[v], INF_CAP)
        net.add_edge(idx_out[v], idx_in[u], INF_CAP)
    return net.max_flow(idx_out[y], idx_in[z])


def route_two(skeleton, d_y, d_z, d, n, union, M, y, z, t_yz, eps=EPS):
    """Route 2: bisect the length cap L on [d, n-1].

    Returns (D2, L_star, probes) where probes = [(L, tau(L)), ...] in probe
    order, D2 = L* + 1 (or +infinity when tau(n-1) = t_yz).
    """
    probes = []

    def check(L):
        val = _tau(L, skeleton, d_y, d_z, union, M, y, z)
        probes.append((L, val))
        return abs(val - t_yz) <= eps

    lo, hi = d, n - 1
    if not check(lo):          # starting self-check: tau(d) = t_yz must hold
        raise RuntimeError("tau(d) != t_yz: the Step 5 result is inconsistent")
    memo = {lo: True}          # probe cache: L=d is known feasible already
    l_star = lo
    while lo <= hi:
        mid = (lo + hi) // 2   # lower midpoint, as traced in the chapter
        if mid in memo:
            ok = memo[mid]
        else:
            ok = check(mid)
            memo[mid] = ok
        if ok:
            l_star = mid
            lo = mid + 1
        else:
            hi = mid - 1
    # When L* reaches the upper bound n-1 a lightest cut severs every y-z
    # walk however long: the signature of a fatal cut, D2 = +infinity.
    return (INF if l_star >= n - 1 else l_star + 1), l_star, probes


def finalize(skeleton, d_y, d_z, union, y, z, d, t_yz, s_min, s_max, M, n, eps=EPS):
    """Finalize: returns (gamma, detail) with
    detail = {D1, d_min, d_max, D2, L_star, probes, D, consistent}.

    d_y / d_z are the Step 4 distance labels on the skeleton (reused, not
    recomputed); d = d_F(y, z); n = |zeta*|.
    """
    d1, (d_min, d_max) = route_one(skeleton, s_min, s_max, y, z)
    d2, l_star, probes = route_two(
        skeleton, d_y, d_z, d, n, union, M, y, z, t_yz, eps
    )
    big = d1 if d1 == INF else d2 if d2 == INF else max(d1, d2)
    if big == INF:
        gamma = (t_yz, 1.0)
    else:
        gamma = (t_yz, 1.0 - d / big)
    detail = {
        "D1": d1, "d_min": d_min, "d_max": d_max,
        "D2": d2, "L_star": l_star, "probes": probes,
        "D": big,
        "consistent": (abs(d1 - d2) <= eps) if (d1 != INF and d2 != INF) else (d1 == d2),
    }
    return gamma, detail
