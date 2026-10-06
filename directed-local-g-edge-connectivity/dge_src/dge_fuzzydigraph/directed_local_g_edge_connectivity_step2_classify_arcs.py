"""Step 2 of Algorithm 6.2: connectivity strength and arc bisection (ClassifyArcs).

Bisects the arc set into strong arcs E_strong and non-strong arcs E_weak:
  E_strong = { a : xi(a) = conn_F(a) }   (strong)
  E_weak   = { a : xi(a) < conn_F(a) }   (non-strong)

Structural criterion: arc u->v is non-strong iff u still reaches v in the
subgraph made of arcs with STRICTLY LARGER membership value.  "Reachable" is
not an equivalence relation, so a union-find is of no use here: the arcs are
sorted by membership value in descending order, grouped by equal value, and
for every arc one reachability search is run on the working subgraph H that
only contains strictly heavier arcs (the whole group is added to H after its
arcs are classified).  O(m (m + n)).

The arc-cut (edge-cut) version has no special case at the end of Step 2: when
y and z are directly linked, the direct arc itself is the lightest (trivial)
cut and the max-flow of Step 5 simply returns xi(y->z).
"""

EPS = 1e-9


def classify_arcs(F, eps=EPS):
    """ClassifyArcs(F): returns (strong, weak).

    strong / weak are lists of (u, v, xi); the two lists together exhaust the
    arc set (no third class exists).
    """
    ordered = sorted(F.arcs.items(), key=lambda kv: kv[1], reverse=True)
    # Group arcs with (numerically) equal membership values.
    groups = []
    for key, xi in ordered:
        if groups and abs(xi - groups[-1][0][1]) <= eps:
            groups[-1].append((key, xi))
        else:
            groups.append([(key, xi)])

    # Working subgraph H: only arcs already judged (strictly heavier groups).
    H = type(F)()
    for v in F.vertices:
        H.ensure_vertex(v)
    strong, weak = [], []
    for group in groups:
        # First classify: H currently holds only strictly heavier arcs.
        for (u, v), xi in group:
            if v in H.reachable(u):
                weak.append((u, v, xi))
            else:
                strong.append((u, v, xi))
        # Then add the whole group at once.
        for (u, v), xi in group:
            H.add_arc(u, v, xi)
    return strong, weak
