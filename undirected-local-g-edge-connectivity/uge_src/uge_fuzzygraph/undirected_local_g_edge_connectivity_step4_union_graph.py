"""Step 4 of Algorithm 5.2: distance labels and the union graph (UnionGraph).

On the skeleton F', with path length counted in EDGES (hops):
  d_y = BFS distances to y,  d_z = BFS distances to z,  d_F(y, z) = d_y[z];
  the union graph F_yz is the subgraph of edges that lie on at least one
  shortest path, collected in one sweep with the tight-edge criterion
      d_y(u) + 1 + d_z(v) == d_F(y, z)   (either direction);
  its vertex set is the endpoints of those edges plus y and z.
No shortest path is ever enumerated (O(n + m), the number of shortest paths
does not enter the running time).
"""

import math

from .undirected_local_g_edge_connectivity_step1_load_graph import FuzzyGraph

INF = math.inf


def bfs_distances(F, source):
    """Hop distances from source over the adjacency lists (BFS layers)."""
    dist = {source: 0}
    queue = [source]
    while queue:
        nxt = []
        for u in queue:
            for w in F.adj[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    nxt.append(w)
        queue = nxt
    return dist


def union_graph(skeleton, y, z):
    """UnionGraph(F', y, z).

    Returns (d, d_y, d_z, F_yz) where F_yz is a FuzzyGraph whose vertices are
    the endpoints of all tight edges plus y and z.
    """
    d_y = bfs_distances(skeleton, y)
    d_z = bfs_distances(skeleton, z)
    if z not in d_y:
        raise ValueError("y and z are not connected in the skeleton F'")
    d = d_y[z]

    F_yz = FuzzyGraph()
    F_yz.ensure_vertex(y)
    F_yz.ensure_vertex(z)
    tight = []
    for (u, v), xi in skeleton.edges.items():
        du = d_y.get(u, INF)
        dv = d_y.get(v, INF)
        zu = d_z.get(u, INF)
        zv = d_z.get(v, INF)
        if du + 1 + zv == d or dv + 1 + zu == d:
            tight.append((u, v, xi))
            F_yz.add_edge(u, v, xi)
    return d, d_y, d_z, F_yz
