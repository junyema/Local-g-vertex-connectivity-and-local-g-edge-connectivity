"""Step 1 of Algorithm 5.1: input and validation (LoadGraph).

Loads an edge table and validates it, exactly as Algorithm 5.1 / Step 1 prescribes:
  - each line has three fields: the two endpoints u v and the membership value xi
    (a line with two fields is the endpoint row "y z"; '#' starts a comment,
    blank lines and commas are ignored);
  - endpoints must be non-empty strings;
  - 0 < xi <= 1, otherwise the membership value is out of range;
  - a duplicate edge must not carry a conflicting membership value
    (no silent overwrite);
  - self-loops (u = v) are dropped at load time and recorded;
  - the graph must be connected (one graph traversal).

Output: a connected fuzzy graph F = (V, zeta, xi) with zeta == 1 and no
self-loops, plus the two distinct endpoints y, z.
"""

EPS = 1e-9


class LoadError(ValueError):
    """Raised when the input violates the conventions of Step 1."""


def _edge_key(u, v):
    return (u, v) if u <= v else (v, u)


class FuzzyGraph:
    """Undirected fuzzy graph F = (V, zeta, xi) stored as adjacency lists."""

    def __init__(self):
        self.vertices = set()          # zeta* (zeta == 1 for every vertex)
        self.edges = {}                # sorted key (u, v) -> xi(u, v)
        self.adj = {}                  # u -> {neighbor: xi}
        self.selfloops_dropped = []    # [(u, v, xi), ...] recorded at load time

    # -- construction -------------------------------------------------------
    def add_edge(self, u, v, xi):
        for w in (u, v):
            self.vertices.add(w)
            self.adj.setdefault(w, {})
        self.edges[_edge_key(u, v)] = xi
        self.adj[u][v] = xi
        self.adj[v][u] = xi

    def ensure_vertex(self, v):
        self.vertices.add(v)
        self.adj.setdefault(v, {})

    # -- queries ------------------------------------------------------------
    def has_edge(self, u, v):
        return _edge_key(u, v) in self.edges

    def xi(self, u, v):
        return self.edges[_edge_key(u, v)]

    def incident(self, v):
        """All edges incident to v inside this graph: [(neighbor, xi), ...]."""
        return sorted(self.adj.get(v, {}).items())

    def edge_list(self):
        """All edges as [(u, v, xi), ...] with u <= v, sorted."""
        return [(u, v, xi) for (u, v), xi in sorted(self.edges.items())]

    def m(self):
        return len(self.edges)

    def n(self):
        return len(self.vertices)

    # -- edits --------------------------------------------------------------
    def remove_edge(self, u, v):
        self.edges.pop(_edge_key(u, v), None)
        if u in self.adj:
            self.adj[u].pop(v, None)
        if v in self.adj:
            self.adj[v].pop(u, None)

    def remove_vertex(self, v):
        for u in list(self.adj.get(v, {})):
            self.remove_edge(u, v)
        self.vertices.discard(v)
        self.adj.pop(v, None)

    def copy(self):
        F = FuzzyGraph()
        F.vertices = set(self.vertices)
        F.edges = dict(self.edges)
        F.adj = {v: dict(nb) for v, nb in self.adj.items()}
        F.selfloops_dropped = list(self.selfloops_dropped)
        return F


def _is_connected(F):
    """One graph traversal: the number of connected components must be 1."""
    if not F.vertices:
        return False
    start = next(iter(F.vertices))
    seen = {start}
    queue = [start]
    while queue:
        u = queue.pop()
        for w in F.adj[u]:
            if w not in seen:
                seen.add(w)
                queue.append(w)
    return len(seen) == len(F.vertices)


def _components(F):
    """All connected components (used in the error message when not connected)."""
    seen = set()
    comps = []
    for v in sorted(F.vertices):
        if v in seen:
            continue
        comp = {v}
        queue = [v]
        seen.add(v)
        while queue:
            u = queue.pop()
            for w in F.adj[u]:
                if w not in seen:
                    seen.add(w)
                    comp.add(w)
                    queue.append(w)
        comps.append(sorted(comp))
    return comps


def parse_edge_table(text):
    """Split the raw text into edge triples and the endpoint row.

    Returns (triples, endpoints) where triples = [(lineno, u, v, xi), ...]
    and endpoints = (y, z) or None.
    """
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


def load_graph_text(text, eps=EPS, require_connected=True):
    """LoadGraph on the raw text of an edge table. Returns (F, y, z)."""
    triples, endpoints = parse_edge_table(text)
    if endpoints is None:
        raise LoadError("no endpoint row 'y z' found after the edge table")
    y, z = endpoints
    if y == z:
        raise LoadError("the two endpoints must be different (y != z)")

    F = FuzzyGraph()
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
        key = _edge_key(u, v)
        if key in seen:
            if abs(seen[key] - xi) > eps:
                raise LoadError(
                    "line %d: duplicate edge %s-%s with conflicting membership "
                    "values (%g vs %g); no silent overwrite" % (lineno, u, v, seen[key], xi)
                )
            continue  # identical duplicate: merge
        seen[key] = xi
        F.add_edge(u, v, xi)

    if not F.vertices:
        raise LoadError(
            "the graph has no vertices"
            + (" (the edge table only contained self-loops)" if F.selfloops_dropped else "")
        )
    for w in (y, z):
        if w not in F.vertices:
            raise LoadError("endpoint '%s' is not in the graph" % w)
    if require_connected and not _is_connected(F):
        comps = _components(F)
        raise LoadError(
            "the graph is not connected (%d components): %s"
            % (len(comps), " | ".join(",".join(c) for c in comps))
        )
    return F, y, z


def load_graph_file(path, eps=EPS, require_connected=True):
    """LoadGraph from a case file. Returns (F, y, z)."""
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    return load_graph_text(text, eps=eps, require_connected=require_connected)
