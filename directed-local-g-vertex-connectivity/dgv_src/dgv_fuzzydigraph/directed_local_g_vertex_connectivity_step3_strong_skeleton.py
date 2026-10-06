"""Step 3 of Algorithm 6.1: drop the non-strong arcs, build the skeleton (F').

StrongSkeleton(F): keep every strong arc, remove every non-strong arc; the
vertex set is unchanged.  conn_{F'}(u, v) = conn_F(u, v) for every ORDERED
pair (u, v), and y still reaches z in F'.
"""

from .directed_local_g_vertex_connectivity_step1_load_digraph import FuzzyDigraph


def strong_skeleton(F, strong_arcs):
    """StrongSkeleton(F): returns the skeleton F' as a FuzzyDigraph.

    strong_arcs is the list of (u, v, xi) produced by Step 2; a linear filter
    rebuilds the spanning subgraph with the vertex set unchanged.
    """
    Fp = FuzzyDigraph()
    for v in F.vertices:
        Fp.ensure_vertex(v)
    for (u, v, xi) in strong_arcs:
        Fp.add_arc(u, v, xi)
    return Fp
