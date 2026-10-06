"""polynomial six-step algorithm (Algorithm 6.1, polynomial version) - directed, vertex cuts.

Package layout mirrors the six steps of Algorithm 6.1:
  directed_local_g_vertex_connectivity_step1_load_digraph.py    LoadDigraph    (input & validation, y reaches z)
  directed_local_g_vertex_connectivity_step2_classify_arcs.py   ClassifyArcs   (connectivity strength & arc bisection)
  directed_local_g_vertex_connectivity_step3_strong_skeleton.py StrongSkeleton (drop non-strong arcs)
  directed_local_g_vertex_connectivity_step4_union_graph.py     UnionGraph     (distance labels & union graph)
  directed_local_g_vertex_connectivity_step5_one_min_cut.py     OneMinCut      (one max-flow: t_yz and extreme cuts)
  directed_local_g_vertex_connectivity_step6_finalize.py        Finalize       (two routes for D and the summary)
  directed_local_g_vertex_connectivity_algorithm_6_1.py            the master pipeline of Algorithm 6.1

Directed vertex-cut version: Step 2 runs one reachability search per arc
("reachable" is not an equivalence relation, no union-find), M(v) of Step 5
takes the OUT-arc minimum only, the special case is triggered only by the
forward strong arc y->z, and all distances are one-way.
"""

__version__ = "2.0.0"
