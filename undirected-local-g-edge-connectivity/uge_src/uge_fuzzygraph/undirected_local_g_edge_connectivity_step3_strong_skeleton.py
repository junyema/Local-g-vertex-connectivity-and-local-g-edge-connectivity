"""Step 3 of Algorithm 5.2: drop the non-strong edges, build the skeleton (F').

StrongSkeleton(F): keep every strong edge, remove every non-strong edge; the
vertex set is unchanged.  The skeleton F' is a spanning subgraph: it is the
union of all maximum spanning trees of F, conn_{F'}(u, v) = conn_F(u, v) for
every pair, and F' is still connected when F is.
"""

from .undirected_local_g_edge_connectivity_step1_load_graph import FuzzyGraph


def strong_skeleton(F, strong_edges):
    """StrongSkeleton(F): returns the skeleton F' as a FuzzyGraph.

    strong_edges is the list of (u, v, xi) produced by Step 2; a linear filter
    rebuilds the spanning subgraph with the vertex set unchanged.
    """
    Fp = FuzzyGraph()
    for v in F.vertices:
        Fp.ensure_vertex(v)
    for (u, v, xi) in strong_edges:
        Fp.add_edge(u, v, xi)
    return Fp
