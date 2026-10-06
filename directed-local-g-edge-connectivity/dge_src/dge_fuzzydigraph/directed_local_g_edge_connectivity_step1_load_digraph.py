"""Step 1 of Algorithm 6.2: input and validation (LoadDigraph).

Loads an arc table and validates it, exactly as Algorithm 6.2 / Step 1 of the
directed documents prescribes:
  - each line has three fields: the two endpoints u v of the arc (u -> v) and
    the membership value xi (a line with two fields is the endpoint row
    "y z"; '#' starts a comment; blank lines and commas are ignored);
  - endpoints must be non-empty strings;
  - 0 < xi <= 1, otherwise the membership value is out of range;
  - a duplicate arc (same ORDERED pair) must not carry a conflicting
    membership value; the two directions of one vertex pair are two different
    arcs, each recorded on its own;
  - self-loops (u = v) are dropped at load time and recorded;
  - y must reach z along the direction of the arcs (one graph traversal) -
    reachability is one-way, "z can reach y" is a different question.

Output: a fuzzy digraph F = (V, zeta, xi) with zeta == 1 and no self-loops,
plus the two distinct endpoints y, z with y reachable z.
"""

EPS = 1e-9


class LoadError(ValueError):
    """Raised when the input violates the conventions of Step 1."""


class FuzzyDigraph:
    """Directed fuzzy graph stored as adjacency lists (out and in)."""

    def __init__(self):
        self.vertices = set()
        self.arcs = {}        # (u, v) -> xi(u, v)
        self.out_adj = {}     # u -> {head: xi}
        self.in_adj = {}      # v -> {tail: xi}
        self.selfloops_dropped = []

    # -- construction -------------------------------------------------------
    def ensure_vertex(self, v):
        self.vertices.add(v)
        self.out_adj.setdefault(v, {})
        self.in_adj.setdefault(v, {})

    def add_arc(self, u, v, xi):
        self.ensure_vertex(u)
        self.ensure_vertex(v)
        self.arcs[(u, v)] = xi
        self.out_adj[u][v] = xi
        self.in_adj[v][u] = xi

    # -- queries ------------------------------------------------------------
    def has_arc(self, u, v):
        return (u, v) in self.arcs

    def xi(self, u, v):
        return self.arcs[(u, v)]

    def out_arcs(self, v):
        """All arcs leaving v inside this graph: [(head, xi), ...]."""
        return sorted(self.out_adj.get(v, {}).items())

    def arc_list(self):
        """All arcs as [(u, v, xi), ...] sorted."""
        return [(u, v, xi) for (u, v), xi in sorted(self.arcs.items())]

    def m(self):
        return len(self.arcs)

    def n(self):
        return len(self.vertices)

    def reversed_graph(self):
        """The graph with every arc reversed (used for the d_z labels)."""
        rev = FuzzyDigraph()
        for v in self.vertices:
            rev.ensure_vertex(v)
        for (u, v), xi in self.arcs.items():
            rev.add_arc(v, u, xi)
        return rev

    def reachable(self, source):
        """The set of vertices reachable from source along the arc directions."""
        seen = {source}
        queue = [source]
        while queue:
            nxt = []
            for u in queue:
                for w in self.out_adj[u]:
                    if w not in seen:
                        seen.add(w)
                        nxt.append(w)
            queue = nxt
        return seen

    # -- edits --------------------------------------------------------------
    def remove_arc(self, u, v):
        self.arcs.pop((u, v), None)
        if u in self.out_adj:
            self.out_adj[u].pop(v, None)
        if v in self.in_adj:
            self.in_adj[v].pop(u, None)

    def remove_vertex(self, v):
        for u in list(self.in_adj.get(v, {})):
            self.remove_arc(u, v)
        for w in list(self.out_adj.get(v, {})):
            self.remove_arc(v, w)
        self.vertices.discard(v)
        self.out_adj.pop(v, None)
        self.in_adj.pop(v, None)

    def copy(self):
        F = FuzzyDigraph()
        F.vertices = set(self.vertices)
        F.arcs = dict(self.arcs)
        F.out_adj = {v: dict(nb) for v, nb in self.out_adj.items()}
        F.in_adj = {v: dict(nb) for v, nb in self.in_adj.items()}
        F.selfloops_dropped = list(self.selfloops_dropped)
        return F


def parse_arc_table(text):
    """Split the raw text into arc triples and the endpoint row."""
    triples = []
    endpoints = None
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        fields = line.replace(",", " ").split()
        if len(fields) == 2:
            if endpoints is not None:
                raise LoadError(
                    "line %d: more than one endpoint row 'y z' found" % lineno
                )
            endpoints = (fields[0], fields[1])
            continue
        if len(fields) != 3:
            raise LoadError(
                "line %d: expected three fields 'u v xi' (or the endpoint row "
                "'y z'), got %d fields" % (lineno, len(fields))
            )
        u, v, val = fields
        if not u or not v:
            raise LoadError("line %d: endpoints must be non-empty strings" % lineno)
        try:
            xi = float(val)
        except ValueError:
            raise LoadError("line %d: membership value '%s' is not a number" % (lineno, val))
        triples.append((lineno, u, v, xi))
    return triples, endpoints


def load_digraph_text(text, eps=EPS):
    """LoadDigraph on the raw text of an arc table. Returns (F, y, z)."""
    triples, endpoints = parse_arc_table(text)
    if endpoints is None:
        raise LoadError("no endpoint row 'y z' found after the arc table")
    y, z = endpoints
    if y == z:
        raise LoadError("the two endpoints must be different (y != z)")

    F = FuzzyDigraph()
    seen = {}
    for lineno, u, v, xi in triples:
        if u == v:
            # Self-loop: dropped at load time and recorded (never an error).
            F.selfloops_dropped.append((u, v, xi))
            continue
        if xi <= 0 or xi > 1:
            raise LoadError(
                "line %d: membership value %g out of range (must satisfy 0 < xi <= 1)"
                % (lineno, xi)
            )
        if (u, v) in seen:
            if abs(seen[(u, v)] - xi) > eps:
                raise LoadError(
                    "line %d: duplicate arc u->v (%s->%s) with conflicting "
                    "membership values (%g vs %g); no silent overwrite"
                    % (lineno, u, v, seen[(u, v)], xi)
                )
            continue  # identical duplicate: merge
        seen[(u, v)] = xi
        F.add_arc(u, v, xi)

    if not F.vertices:
        raise LoadError(
            "the graph has no vertices"
            + (" (the arc table only contained self-loops)" if F.selfloops_dropped else "")
        )
    for w in (y, z):
        if w not in F.vertices:
            raise LoadError("endpoint '%s' is not in the graph" % w)
    if z not in F.reachable(y):
        raise LoadError(
            "y cannot reach z in the directed graph; the vertices reachable "
            "from y are: %s" % ", ".join(sorted(F.reachable(y)))
        )
    return F, y, z


def load_digraph_file(path, eps=EPS):
    """LoadDigraph from a case file. Returns (F, y, z)."""
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    return load_digraph_text(text, eps=eps)
