"""polynomial six-step algorithm (Algorithm 6.2, polynomial version) - directed, arc cuts.

Package layout mirrors the six steps of Algorithm 6.2:
  directed_local_g_edge_connectivity_step1_load_digraph.py    LoadDigraph    (input & validation, y reaches z)
  directed_local_g_edge_connectivity_step2_classify_arcs.py   ClassifyArcs   (connectivity strength & arc bisection)
  directed_local_g_edge_connectivity_step3_strong_skeleton.py StrongSkeleton (drop non-strong arcs)
  directed_local_g_edge_connectivity_step4_union_graph.py     UnionGraph     (distance labels & union graph)
  directed_local_g_edge_connectivity_step5_one_min_cut.py     OneMinCut      (one max-flow: t'_yz and extreme cuts)
  directed_local_g_edge_connectivity_step6_finalize.py        Finalize       (two routes for D and the summary)
  directed_local_g_edge_connectivity_algorithm_6_2.py            the master pipeline of Algorithm 6.2

Directed arc-cut version: only arcs are removed (the vertex count never
changes), Step 2 runs one reachability search per arc (no union-find), the
network of Step 5 puts xi(e) on the union arcs with their direction kept,
and there is no strong-arc special case (a directly linked y-z pair is the
trivial solution t' = xi(y->z), not a degenerate case).
"""

__version__ = "2.0.0"
