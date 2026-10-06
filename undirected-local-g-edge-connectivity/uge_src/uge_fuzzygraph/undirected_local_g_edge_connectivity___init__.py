"""polynomial six-step algorithm (Algorithm 5.2, polynomial version) - undirected, edge cuts.

Package layout mirrors the six steps of Algorithm 5.2:
  undirected_local_g_edge_connectivity_step1_load_graph.py      LoadGraph      (input & validation)
  undirected_local_g_edge_connectivity_step2_classify_edges.py  ClassifyEdges  (connectivity strength & edge bisection)
  undirected_local_g_edge_connectivity_step3_strong_skeleton.py StrongSkeleton (drop non-strong edges)
  undirected_local_g_edge_connectivity_step4_union_graph.py     UnionGraph     (distance labels & union graph)
  undirected_local_g_edge_connectivity_step5_one_min_cut.py     OneMinCut      (one max-flow: t'_yz and extreme cuts)
  undirected_local_g_edge_connectivity_step6_finalize.py        Finalize       (two routes for D and the summary)
  undirected_local_g_edge_connectivity_algorithm_5_2.py            the master pipeline of Algorithm 5.2

Edge-cut version: only edges are removed (the vertex count never changes),
the network of Step 5 puts the membership value xi(e) on the arcs, and there
is no strong-link special case (a directly linked y-z pair is the trivial
solution t' = xi(yz), not a degenerate case).
"""

__version__ = "2.0.0"
