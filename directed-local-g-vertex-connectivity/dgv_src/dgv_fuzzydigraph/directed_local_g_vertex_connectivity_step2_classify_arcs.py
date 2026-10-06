"""Step 2 of Algorithm 6.1: connectivity strength and arc bisection (ClassifyArcs).

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

Direction matters twice: xi(u,v) and xi(v,u) are judged separately, and the
special case at the end of Step 2 is triggered ONLY by the forward strong arc
y->z (a strong arc z->y alone does not trigger it).
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


def strong_link_between(F, y, z, strong):
    """Special case at the end of Step 2 (directed vertex-cut version).

    If the forward arc y->z exists and is strong, no vertex cut exists
    (endpoints may not enter a cut) and Algorithm 6.1 returns the conventional
    value  gamma_yz = ((|zeta*| - 1) * xi(y, z), 0)  and terminates.

    A strong arc z->y alone (without y->z) does NOT trigger the special case.

    Returns the pair, or None when the flow continues into Step 3.
    """
    if F.has_arc(y, z):
        strong_keys = {(u, v) for (u, v, _) in strong}
        if (y, z) in strong_keys:
            n = len(F.vertices)
            return ((n - 1) * F.xi(y, z), 0.0)
    return None
