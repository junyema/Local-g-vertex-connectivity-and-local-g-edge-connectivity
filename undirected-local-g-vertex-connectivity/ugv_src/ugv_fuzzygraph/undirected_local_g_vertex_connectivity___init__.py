"""polynomial six-step algorithm (Algorithm 5.1, polynomial version) - undirected, vertex cuts.

Package layout mirrors the six steps of Algorithm 5.1:
  undirected_local_g_vertex_connectivity_step1_load_graph.py      LoadGraph      (input & validation)
  undirected_local_g_vertex_connectivity_step2_classify_edges.py  ClassifyEdges  (connectivity strength & edge bisection)
  undirected_local_g_vertex_connectivity_step3_strong_skeleton.py StrongSkeleton (drop non-strong edges)
  undirected_local_g_vertex_connectivity_step4_union_graph.py     UnionGraph     (distance labels & union graph)
  undirected_local_g_vertex_connectivity_step5_one_min_cut.py     OneMinCut      (one max-flow: t_yz and extreme cuts)
  undirected_local_g_vertex_connectivity_step6_finalize.py        Finalize       (two routes for D and the summary)
  undirected_local_g_vertex_connectivity_algorithm_5_1.py            the master pipeline of Algorithm 5.1
"""

__version__ = "2.0.0"
