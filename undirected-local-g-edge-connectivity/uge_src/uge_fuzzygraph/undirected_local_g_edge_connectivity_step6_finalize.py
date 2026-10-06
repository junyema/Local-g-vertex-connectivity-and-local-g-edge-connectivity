"""Step 6 of Algorithm 5.2: the two routes for D and the summary (Finalize).

D = max_{S in C*} d_{F'-S}(y, z)  (+infinity when C* contains a fatal cut);
S here is an EDGE cut: F' - S removes edges only, the vertex count never
changes.

Route 1 (extreme minimum cuts + two BFS): delete S_min, then S_max, from the
skeleton, measure d_{F'-S}(y, z) by BFS, take the larger value -> D1.

Route 2 (length-cap bisection): tau(L) is the least weight of an edge cut,
taken on union-graph edges only, that severs every y-z walk of length <= L.
An edge belongs to H_L iff min{d_y(u)+1+d_z(v), d_y(v)+1+d_z(u)} <= L; in the
H_L network every edge keeps its direction-pair arcs; an H_L edge that belongs
to the union graph gets the capacity xi(e), every structure edge outside the
union graph gets a +infinity sentinel and cannot be cut.  tau is
non-decreasing, tau(D) = t'_yz, so {L : tau(L) = t'_yz} is a prefix [D, L*];
bisecting on [d, n-1] with O(log n) min-cuts yields L*, and D2 = L* + 1
(D2 = +infinity when tau(n-1) is still t'_yz, the signature of a fatal cut).

Summary: t'_yz is always finite (deleting every edge incident to y is a
finite edge cut of the union graph), so the two branches of the summary are
always well defined: D = max(D1, D2), and gamma'_yz = (t'_yz, 1) when
D = +infinity (a fatal cut exists), else (t'_yz, 1 - d_F(y,z)/D).
"""

import math

from .undirected_local_g_edge_connectivity_step4_union_graph import bfs_distances
from .undirected_local_g_edge_connectivity_step5_one_min_cut import Dinic, INF_CAP

INF = math.inf
EPS = 1e-9


def _d_after_edge_removal(skeleton, removed_keys, y, z):
    """BFS on F' - S (S an edge set given as sorted key pairs)."""
    work = skeleton.copy()
    for (u, v) in removed_keys:
        work.remove_edge(u, v)
    dist = bfs_distances(work, y)
    return dist.get(z, INF)


def route_one(skeleton, s_min, s_max, y, z):
    """Route 1: delete the extreme minimum edge cuts, BFS twice, take larger."""
    d_min = _d_after_edge_removal(skeleton, [(u, v) for (u, v, _) in s_min], y, z)
    d_max = _d_after_edge_removal(skeleton, [(u, v) for (u, v, _) in s_max], y, z)
    return max(d_min, d_max), (d_min, d_max)


def _tau(L, skeleton, d_y, d_z, union, y, z):
    """tau(L): one minimum cut on H_L whose cut elements are the union-graph
    edges only (structure edges outside the union graph carry the sentinel)."""
    h_edges = {}
    for (u, v), xi in skeleton.edges.items():
        du = d_y.get(u, INF)
        dv = d_y.get(v, INF)
        zu = d_z.get(u, INF)
        zv = d_z.get(v, INF)
        if min(du + 1 + zv, dv + 1 + zu) <= L:
            cap = xi if (u, v) in union.edges else INF_CAP
            h_edges[(u, v)] = cap

    order = sorted({w for e in h_edges for w in e} | {y, z})
    idx = {v: i for i, v in enumerate(order)}
    net = Dinic(len(order))
    for (u, v), cap in h_edges.items():
        net.add_edge(idx[u], idx[v], cap)
        net.add_edge(idx[v], idx[u], cap)
    return net.max_flow(idx[y], idx[z])


def route_two(skeleton, d_y, d_z, d, n, union, y, z, t_yz, eps=EPS):
    """Route 2: bisect the length cap L on [d, n-1].

    Returns (D2, L_star, probes); D2 = L* + 1, or +infinity when
    tau(n-1) = t'_yz.
    """
    probes = []

    def check(L):
        val = _tau(L, skeleton, d_y, d_z, union, y, z)
        probes.append((L, val))
        return abs(val - t_yz) <= eps

    lo, hi = d, n - 1
    if not check(lo):          # starting self-check: tau(d) = t'_yz must hold
        raise RuntimeError("tau(d) != t'_yz: the Step 5 result is inconsistent")
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


def finalize(skeleton, d_y, d_z, union, y, z, d, t_yz, s_min, s_max, n, eps=EPS):
    """Finalize: returns (gamma, detail).  t'_yz is always finite (Algorithm 7
    has no t' = +infinity branch), so gamma is always a proper pair."""
    d1, (d_min, d_max) = route_one(skeleton, s_min, s_max, y, z)
    d2, l_star, probes = route_two(skeleton, d_y, d_z, d, n, union, y, z, t_yz, eps)
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
