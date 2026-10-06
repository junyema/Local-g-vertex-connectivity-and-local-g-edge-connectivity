"""Step 4 of Algorithm 6.2: distance labels and the union graph (UnionGraph).

On the skeleton F', with path length counted in ARCS (hops):
  d_y = BFS from y on F' (whom y can reach);
  d_z = BFS from z on the REVERSED graph (F')^rev (who can reach z) - running
        the BFS from z on the original graph would answer "whom z can reach",
        a different question on a directed graph;
  d_F(y, z) = d_y[z];
  the union graph F_yz is the subdigraph of arcs that lie on at least one
  shortest path, collected in one sweep with the tight-arc criterion
      d_y(u) + 1 + d_z(v) == d_F(y, z)      (each arc in ITS OWN direction);
  its vertex set is the endpoints of those arcs plus y and z.
F_yz is a layered directed acyclic graph: every arc goes from layer k to
layer k+1.  No shortest path is ever enumerated (O(n + m)).
"""

import math

from .directed_local_g_edge_connectivity_step1_load_digraph import FuzzyDigraph

INF = math.inf


def bfs_distances(F, source):
    """Hop distances from source over the out-adjacency (BFS layers)."""
    dist = {source: 0}
    queue = [source]
    while queue:
        nxt = []
        for u in queue:
            for w in F.out_adj[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    nxt.append(w)
        queue = nxt
    return dist


def union_graph(skeleton, y, z):
    """UnionGraph(F', y, z) for a directed skeleton.

    Returns (d, d_y, d_z, F_yz) where F_yz is a FuzzyDigraph whose vertices
    are the endpoints of all tight arcs plus y and z.
    """
    d_y = bfs_distances(skeleton, y)
    d_z = bfs_distances(skeleton.reversed_graph(), z)   # reverse-graph BFS
    if z not in d_y:
        raise ValueError("y cannot reach z in the skeleton F'")
    d = d_y[z]

    F_yz = FuzzyDigraph()
    F_yz.ensure_vertex(y)
    F_yz.ensure_vertex(z)
    for (u, v), xi in skeleton.arcs.items():
        if d_y.get(u, INF) + 1 + d_z.get(v, INF) == d:
            F_yz.add_arc(u, v, xi)
    return d, d_y, d_z, F_yz
