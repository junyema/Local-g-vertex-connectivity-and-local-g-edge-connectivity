"""Per-step evolution diagrams for Algorithm 5.1 (pure SVG, no dependencies).

The diagrams use the FIGURE STYLE OF THE CHAPTER's own figures
(chapter figures): the same per-case vertex layout copied from the chapter, edge
thickness proportional to xi, light-blue round vertices with a dark-blue
outline, small white weight plates, red highlights for cuts and the
document's green/red component colouring.  The two endpoints y and z sit at
the LEFT and RIGHT of the picture, exactly as in the chapter.

  step1  LoadGraph       the input fuzzy graph F (xi written on every edge)
  step2  ClassifyEdges   strong edges vs non-strong edges (special case noted)
  step3  StrongSkeleton  the strong skeleton F' (vertex set unchanged)
  step4  UnionGraph      the union graph F_yz, distance labels d_y / d_z
  step5  OneMinCut       the union graph F_yz with the minimum cut and t_yz
  step6  Finalize        F' minus the extreme cut S_min, plus gamma_yz

Every method returns an SVG string; undirected_local_g_vertex_connectivity_algorithm_5_1.py stores them in
CaseResult.diagrams and run.py writes them next to the step reports, one
`stepN_*.svg` per step plus an ordered `evolution.html` gallery.

The vertex-cut and edge-cut variants share this module: pass
vertex_cut=True for the vertex version (S is a vertex set) and
vertex_cut=False for the edge version (S is an edge set).
"""

import math

from .undirected_local_g_vertex_connectivity_step_layouts import lookup

# ---------------------------------------------------------------- geometry --
_CANVAS_W, _CANVAS_H = 780, 640
_AREA = (30.0, 100.0, 750.0, 534.0)      # drawing area (x0, y0, x1, y1)
_NODE_R = 13.0
_SAG = 0.085                             # bend sagitta / chord (chapter: 18 deg)

# --------------------------------------------------- docs palette (xcolor) --
_NODE_FILL = "#EBEBFF"                   # blue!8
_NODE_STROKE = "#00008C"                 # blue!55!black
_EDGE = "#737373"                        # black!55
_EDGE_FAINT = "#D4D4D4"
_STRONG = "#33566E"                      # rgb 51,86,110 (document strong edge)
_WEAK_DASH = "#9A8FB4"                   # rgb 154,143,180 (document weak arc)
_CUT = "#B20000"                         # red!70!black
_COMP_Y = ("#E4F1E6", "#2E7D4F", "#1B4A30")   # green family (y's side)
_COMP_Z = ("#FBE4E4", "#C0392B", "#7B1A1A")   # red family (z's side)
_OTHER = ("#EDEDED", "#8A8A8A", "#444444", 1.4)
_TXT = "#1A1A1A"

EPS = 1e-9


def _esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _fmt_xi(xi):
    return "%g" % xi


def _fmt_val(v):
    if v == math.inf:
        return "+inf"
    if isinstance(v, float) and v >= 1e10:
        return "+inf"
    return "%g" % v


def _sorted_names(names):
    def key(v):
        s = str(v)
        return (0, int(s), "") if s.lstrip("-").isdigit() else (1, 0, s)
    return sorted(names, key=key)


def _uk(u, v):
    """Canonical undirected key: the alphabetically smaller name first."""
    return (u, v) if str(u) <= str(v) else (v, u)


def _edge_width(xi):
    """Document convention: line width grows linearly with xi (pt)."""
    return 0.55 + 2.75 * xi


def _fit(raw):
    """Map document coordinates (y up) onto the canvas (y down)."""
    xs = [p[0] for p in raw.values()]
    ys = [p[1] for p in raw.values()]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, h = (x1 - x0) or 1.0, (y1 - y0) or 1.0
    ax0, ay0, ax1, ay1 = _AREA
    s = min((ax1 - ax0) / w, (ay1 - ay0) / h)
    ox = (ax0 + ax1) / 2.0 - s * (x0 + x1) / 2.0
    oy = (ay0 + ay1) / 2.0 + s * (y0 + y1) / 2.0
    return (lambda p: (ox + s * p[0], oy - s * p[1])), s


def _trim(p1, p2, r1, r2):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    dist = math.hypot(dx, dy)
    if dist < 1e-9:
        return p1, p2
    ux, uy = dx / dist, dy / dist
    return ((p1[0] + ux * r1, p1[1] + uy * r1),
            (p2[0] - ux * r2, p2[1] - uy * r2))


def _line(p1, p2, color, width, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.2f"%s stroke-linecap="round"/>'
            % (p1[0], p1[1], p2[0], p2[1], color, width, d))


def _xi_label(pt, text):
    """A small white weight plate, as in the chapter's weight style."""
    w, h = 13 + 6.6 * len(text), 14
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" rx="2" '
            'fill="#ffffff" fill-opacity="0.95"/>'
            '<text x="%.1f" y="%.1f" font-size="10" fill="#333333" '
            'text-anchor="middle">%s</text>'
            % (pt[0] - w / 2, pt[1] - h / 2, w, h, pt[0], pt[1] + 3.5,
               _esc(text)))


def _node(v, p, fill, stroke, tcol, width=1.6):
    out = ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
           'stroke-width="%.2f"/>' % (p[0], p[1], _NODE_R, fill, stroke, width))
    out += ('<text x="%.1f" y="%.1f" font-size="12" fill="%s" '
            'text-anchor="middle">%s</text>'
            % (p[0], p[1] + 4, tcol, _esc(v)))
    return out


def _sub(pt, text):
    return ('<text x="%.1f" y="%.1f" font-size="9.5" fill="#667788" '
            'text-anchor="middle" font-family="Consolas, monospace">%s</text>'
            % (pt[0], pt[1] + _NODE_R + 11, _esc(text)))


def _header(title, subtitle):
    return ('<text x="24" y="34" font-size="18" font-weight="bold" '
            'fill="#0f172a">%s</text>'
            '<text x="24" y="54" font-size="12" fill="#64748b">%s</text>'
            % (_esc(title), _esc(subtitle)))


def _banner(lines):
    x, y0, lh = 24, _CANVAS_H - 24 - 17 * len(lines), 17
    h = 14 + 17 * len(lines)
    out = ('<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="#f8fafc" '
           'stroke="#cbd5e1"/>' % (x, y0, _CANVAS_W - 2 * x, h))
    for i, ln in enumerate(lines):
        out += ('<text x="%d" y="%.1f" font-size="12" fill="#334155" '
                'font-family="Consolas, monospace">%s</text>'
                % (x + 12, y0 + 19 + i * lh, _esc(ln)))
    return out


def _legend(items, y=72):
    out = []
    x = 26
    for color, dash, label in items:
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" '
                   'stroke-width="3"%s stroke-linecap="round"/>'
                   % (x, y, x + 24, y, color, d))
        out.append('<text x="%d" y="%d" font-size="11" fill="#475569">%s</text>'
                   % (x + 30, y + 4, _esc(label)))
        x += 30 + 6.6 * len(label) + 24
    return "".join(out)


def _svg_wrap(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 %d %d" font-family="Segoe UI, Arial, sans-serif">'
            '<rect width="%d" height="%d" fill="#ffffff"/>%s</svg>'
            % (_CANVAS_W, _CANVAS_H, _CANVAS_W, _CANVAS_H,
               _CANVAS_W, _CANVAS_H, body))


class Diagrams:
    """One diagram per step of Algorithm 5.1, all on the chapter's layout."""

    def __init__(self, F, y, z, vertex_cut=True, case=""):
        self.F = F
        self.y, self.z = y, z
        self.vertex_cut = vertex_cut
        self.keys = {_uk(u, v) for (u, v, _) in F.edge_list()}
        data = lookup(F.vertices)
        if data is not None:
            self.raw = data["pos"]
            self.lab_raw = data["labels"]
        else:                                    # custom file: circle layout
            self.raw = self._circle_raw(F, y, z)
            self.lab_raw = {}
        self.map, self.scale = _fit(self.raw)
        self.pos = {v: self.map(p) for v, p in self.raw.items()}
        self.labels = {_uk(*kv): self.map((x, y))
                       for kv, (x, y, _) in self.lab_raw.items()}
        self.vals = {_uk(*kv): val
                     for kv, (_, _, val) in self.lab_raw.items()}

    @staticmethod
    def _circle_raw(F, y, z):
        """Auto layout for cases without a document layout: y is the
        leftmost vertex and z the rightmost one, on a horizontal axis;
        the other vertices alternate between an arc above and an arc
        below that axis (upper arc first)."""
        others = [v for v in _sorted_names(F.vertices) if v not in (y, z)]
        k = len(others)
        up = (k + 1) // 2
        out = {y: (0.0, 4.2), z: (13.0, 4.2)}
        for i, v in enumerate(others):
            upper = (i % 2 == 0)
            m = up if upper else k // 2
            idx = i // 2
            ang = math.radians(180.0 - 180.0 * (idx + 1) / (m + 1))
            x = 6.5 + 6.5 * math.cos(ang)
            yy = 4.2 + (3.4 if upper else -3.4) * math.sin(ang)
            out[v] = (x, yy)
        return out

    # -- label helpers --------------------------------------------------------
    def _label_pt(self, kv, u, v, xi):
        pt = self.labels.get(kv) or self.labels.get(_uk(u, v))
        if pt is None:
            a, b = self.pos[u], self.pos[v]
            pt = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 11)
        return _xi_label(pt, self.vals.get(kv) or _fmt_xi(xi))

    # -- drawing --------------------------------------------------------------
    def _draw(self, styled, bend_keys=()):
        """styled: [(kv, u, v, xi, color, width, dash)]; bend_keys: kv set."""
        parts = []
        for kv, u, v, xi, color, width, dash in styled:
            if kv in bend_keys:
                parts.append(self._bend_arc(u, v, color, width, dash))
            else:
                p1, p2 = _trim(self.pos[u], self.pos[v],
                               _NODE_R + 2.5, _NODE_R + 2.5)
                parts.append(_line(p1, p2, color, width, dash))
        for kv, u, v, xi, color, width, dash in styled:
            parts.append(self._label_pt(kv, u, v, xi))
        return "".join(parts)

    def _bend_arc(self, u, v, color, width, dash):
        """Quadratic arc with the chapter's bend-left=18 side (y-up)."""
        a, b = self.raw[u], self.raw[v]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        cx, cy = mx - dy / L * _SAG * L, my + dx / L * _SAG * L
        A, B, C = self.map(a), self.map(b), self.map((cx, cy))
        A = _trim(A, C, _NODE_R + 2.5, 0)[0]
        B = _trim(B, C, _NODE_R + 2.5, 0)[0]
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        return ('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                'stroke="%s" stroke-width="%.2f"%s stroke-linecap="round"/>'
                % (A[0], A[1], C[0], C[1], B[0], B[1], color, width, d))

    def _draw_nodes(self, node_style=None, node_sub=None, only=None):
        """node_style: {v: (fill, stroke, text_color, line_width)}."""
        parts = []
        for v in _sorted_names(only if only is not None else self.F.vertices):
            style = node_style.get(v) if node_style else None
            fill, stroke, tcol, lw = style or (_NODE_FILL, _NODE_STROKE,
                                               _TXT, 1.6)
            parts.append(_node(v, self.pos[v], fill, stroke, tcol, lw))
            if node_sub and v in node_sub:
                parts.append(_sub(self.pos[v], node_sub[v]))
        return "".join(parts)

    # -- Step 1 --------------------------------------------------------------
    def step1(self):
        loops = getattr(self.F, "selfloops_dropped", [])
        loop_txt = ", ".join("%s-%s(%g)" % sl for sl in loops) if loops else "none"
        title = "Step 1 - LoadGraph: the input fuzzy graph F"
        sub = ("n = %d vertices, m = %d edges, connected;  self-loops dropped: %s"
               % (self.F.n(), self.F.m(), loop_txt))
        styled = []
        for (u, v), xi in self.F.edges.items():
            kv = _uk(u, v)
            styled.append((kv, u, v, xi, _EDGE, _edge_width(xi), None))
        body = _header(title, sub)
        body += _legend([(_EDGE, None, "edge, thickness ~ xi")])
        body += '<g>%s</g>' % self._draw(styled)
        body += '<g>%s</g>' % self._draw_nodes()
        body += _banner([
            "y = %s (left), z = %s (right): the two endpoints of the local"
            % (self.y, self.z),
            "connectivity problem; path length is counted in edges (hops).",
        ])
        return _svg_wrap(body)

    # -- Step 2 --------------------------------------------------------------
    def step2(self, strong, weak, special):
        title = "Step 2 - ClassifyEdges: strong vs non-strong edges"
        sub = ("strong edges: xi(e) = conn_F(e)  (dark blue)   |   "
               "non-strong edges: xi(e) < conn_F(e)  (grey)")
        smap = {_uk(u, v) for (u, v, _) in strong}
        styled = []
        for (u, v), xi in self.F.edges.items():
            kv = _uk(u, v)
            if kv in smap:
                styled.append((kv, u, v, xi, _STRONG, 2.6, None))
            else:
                styled.append((kv, u, v, xi, _EDGE, _edge_width(xi), "5 3"))
        body = _header(title, sub)
        legend = [(_STRONG, None, "strong")]
        if weak:
            legend.append((_EDGE, "5 3", "non-strong"))
        body += _legend(legend)
        body += '<g>%s</g>' % self._draw(styled)
        body += '<g>%s</g>' % self._draw_nodes()
        lines = ["strong edges: %d   non-strong edges: %d"
                 % (len(strong), len(weak))]
        if special is not None:
            lines += [
                "SPECIAL CASE: the endpoint edge %s-%s is a STRONG edge;"
                % (self.y, self.z),
                "no vertex cut exists, Algorithm 5.1 returns the conventional",
                "value gamma_yz = ((|zeta*| - 1) * xi(y,z), 0) = %s and stops."
                % _fmt_gamma_pair(special),
            ]
        elif self.vertex_cut:
            lines.append("special case not triggered: y-z is not a strong edge.")
        else:
            lines.append("no special case in the edge-cut version "
                         "(a direct y-z edge is the trivial lightest cut).")
        body += _banner(lines)
        return _svg_wrap(body)

    # -- Step 3 --------------------------------------------------------------
    def step3(self, Fp):
        title = "Step 3 - StrongSkeleton: drop the non-strong edges"
        sub = ("skeleton F':  n = %d vertices (UNCHANGED),  m = %d edges "
               "(strong edges only)" % (Fp.n(), Fp.m()))
        styled = []
        for (u, v), xi in Fp.edges.items():
            kv = _uk(u, v)
            styled.append((kv, u, v, xi, _EDGE, _edge_width(xi), None))
        body = _header(title, sub)
        body += _legend([(_EDGE, None, "strong edge kept in F'")])
        body += '<g>%s</g>' % self._draw(styled)
        body += '<g>%s</g>' % self._draw_nodes()
        body += _banner([
            "the vertex set does not change; every further step runs on F'.",
        ])
        return _svg_wrap(body)

    # -- Step 4 --------------------------------------------------------------
    def step4(self, Fp, F_yz, d_y, d_z, d):
        title = "Step 4 - UnionGraph: the tight edges of F'"
        sub = ("d_F(y,z) = %s hops;  tight edge: d_y(u) + 1 + d_z(v) = d_F(y,z)"
               " (either direction)" % _fmt_val(d))
        tight = {_uk(u, v) for (u, v) in F_yz.edges.keys()}
        styled = []
        for (u, v), xi in Fp.edges.items():
            kv = _uk(u, v)
            if kv in tight:
                styled.append((kv, u, v, xi, _EDGE, _edge_width(xi) + 0.5,
                               None))
            else:
                styled.append((kv, u, v, xi, _EDGE_FAINT, 1.2, None))
        subs = {}
        for v in Fp.vertices:
            dy = _fmt_val(d_y[v]) if v in d_y else "inf"
            dz = _fmt_val(d_z[v]) if v in d_z else "inf"
            subs[v] = "dy=%s dz=%s" % (dy, dz)
        body = _header(title, sub)
        legend = [(_EDGE, None, "tight edge -> union graph F_yz")]
        if len(tight) < Fp.m():
            legend.append((_EDGE_FAINT, None, "not on any shortest path"))
        body += _legend(legend)
        body += '<g>%s</g>' % self._draw(styled)
        body += '<g>%s</g>' % self._draw_nodes(node_sub=subs)
        body += _banner([
            "d_y = BFS distances to y,  d_z = BFS distances to z  (on F',",
            "hop counts);  F_yz collects the tight edges only: |V| = %d, "
            "|E| = %d." % (F_yz.n(), F_yz.m()),
        ])
        return _svg_wrap(body)

    # -- Step 5 --------------------------------------------------------------
    def step5(self, F_yz, t_yz, s_min, s_max):
        t_name = "t_yz" if self.vertex_cut else "t'_yz"
        title = "Step 5 - OneMinCut: %s from ONE max-flow" % t_name
        if self.vertex_cut:
            sub = ("split network with capacities M(v);  source y_out, sink z_in"
                   "  (no edge cut is ever enumerated)")
        else:
            sub = ("every union edge bidirectionalized, arc capacity xi(e);"
                   "  source y, sink z  (no enumeration)")
        cut_keys = self._cut_keys(s_min)
        styled = []
        for (u, v), xi in F_yz.edges.items():
            kv = _uk(u, v)
            if kv in cut_keys:
                styled.append((kv, u, v, xi, _CUT, _edge_width(xi) + 0.6,
                               None))
            else:
                styled.append((kv, u, v, xi, _EDGE, _edge_width(xi), None))
        smin_set = set(s_min) if self.vertex_cut else set()
        node_style = {}
        for v in F_yz.vertices:
            if v in smin_set:
                node_style[v] = (_COMP_Z[0], _COMP_Z[1], _COMP_Z[2], 1.8)
        only = set(F_yz.vertices)
        body = _header(title, sub)
        legend = [(_EDGE, None, "union edge"),
                  (_CUT, None, "minimum cut")]
        if self.vertex_cut:
            legend.append((_COMP_Z[1], None, "S_min (source side)"))
        body += _legend(legend)
        body += '<g>%s</g>' % self._draw(styled)
        body += '<g>%s</g>' % self._draw_nodes(node_style=node_style, only=only)
        if self.vertex_cut:
            lines = [
                "t_yz = %s" % _fmt_val(t_yz),
                "S_min (source side) = {%s}" % ", ".join(s_min),
                "S_max (sink side)   = {%s}" % ", ".join(s_max),
            ]
        else:
            lines = [
                "t'_yz = %s" % _fmt_val(t_yz),
                "S_min (source side) = %s" % _fmt_edge_cut(s_min),
                "S_max (sink side)   = %s" % _fmt_edge_cut(s_max),
            ]
        body += _banner(lines)
        return _svg_wrap(body)

    def _cut_keys(self, s_min):
        if not self.vertex_cut:
            return {_uk(u, v) for (u, v, _) in s_min}
        smin = set(s_min)
        return {kv for kv in self.keys
                if (kv[0] in smin) != (kv[1] in smin)}

    # -- Step 6 --------------------------------------------------------------
    def step6(self, Fp, s_min, det, gamma, d):
        title = "Step 6 - Finalize: the extreme cut deleted and gamma_yz"
        work = Fp.copy()
        if self.vertex_cut:
            for v in s_min:
                work.remove_vertex(v)
        else:
            for (u, v, _) in s_min:
                work.remove_edge(u, v)
        comp = _components(work, self.y)
        y_comp = comp.get(self.y, set())
        z_comp = comp.get(self.z, set())
        node_style = {}
        for v in work.vertices:
            if v in y_comp:
                node_style[v] = (_COMP_Y[0], _COMP_Y[1], _COMP_Y[2], 1.7)
            elif v in z_comp:
                node_style[v] = (_COMP_Z[0], _COMP_Z[1], _COMP_Z[2], 1.7)
            else:
                node_style[v] = (_OTHER[0], _OTHER[1], _OTHER[2], 1.4)
        if self.vertex_cut:
            removed_v = set(s_min)
            kept = [(_uk(u, v), u, v, xi) for (u, v), xi in Fp.edges.items()
                    if u not in removed_v and v not in removed_v]
        else:
            cut = {_uk(u, v) for (u, v, _) in s_min}
            kept = [(_uk(u, v), u, v, xi) for (u, v), xi in Fp.edges.items()
                    if _uk(u, v) not in cut]
        styled = [(kv, u, v, xi, _EDGE, _edge_width(xi), None)
                  for (kv, u, v, xi) in kept]
        ghosts = []
        if not self.vertex_cut:
            for (u, v, _) in s_min:
                p1, p2 = _trim(self.pos[u], self.pos[v],
                               _NODE_R + 2.5, _NODE_R + 2.5)
                ghosts.append(_line(p1, p2, _CUT, 1.4, "4 3"))
        body = _header(title, "route 1 shown: delete S_min from F' and "
                              "measure the new y-z distance by BFS")
        legend = []
        if y_comp:
            legend.append((_COMP_Y[1], None, "y's component"))
        if z_comp and z_comp is not y_comp:
            legend.append((_COMP_Z[1], None, "z's component"))
        if ghosts:
            legend.append((_CUT, "4 3", "deleted by the cut"))
        body += _legend(legend)
        body += '<g>%s</g>' % "".join(ghosts)
        body += '<g>%s</g>' % self._draw(styled)
        body += '<g>%s</g>' % self._draw_nodes(node_style=node_style,
                                               only=set(work.vertices))
        fatal = det["D"] == math.inf
        g_name = "gamma_yz" if self.vertex_cut else "gamma'_yz"
        t_name = "t_yz" if self.vertex_cut else "t'_yz"
        if self.vertex_cut:
            head = ("delete S_min = {%s} -> d = %s    D1 = %s"
                    % (", ".join(s_min), _fmt_val(det["d_min"]),
                       _fmt_val(det["D1"])))
        else:
            head = ("delete S_min -> d = %s        D1 = %s"
                    % (_fmt_val(det["d_min"]), _fmt_val(det["D1"])))
        lines = [
            head,
            "D2 (length-cap bisection) = %s      D = max(D1, D2) = %s"
            % (_fmt_val(det["D2"]), _fmt_val(det["D"])),
        ]
        if det["d_min"] == math.inf:
            lines.append("FATAL: y and z are disconnected in F' - S_min "
                         "-> eta = 1")
        elif fatal:
            lines.append("FATAL via route 2: a middle member of the lightest"
                         " family is fatal -> eta = 1")
        lines.append("%s = (%s, 1 - d/D) = (%s, %s)"
                     % (g_name, t_name,
                        _fmt_val(gamma[0]), _fmt_val(gamma[1])))
        body += _banner(lines)
        return _svg_wrap(body)


# ------------------------------------------------------------------ helpers --
def _fmt_gamma_pair(gamma):
    t, eta = gamma
    return "(%s, %s)" % (_fmt_val(t), _fmt_val(eta))


def _fmt_edge_cut(s):
    return "{%s}" % ", ".join("%s-%s(%g)" % (u, v, xi) for (u, v, xi) in s)


def _components(G, y):
    """{v: representative set} of the connected components of G."""
    comp_of = {}
    for v in _sorted_names(G.vertices):
        if v in comp_of:
            continue
        comp = {v}
        queue = [v]
        comp_of[v] = comp
        while queue:
            u = queue.pop()
            for w in G.adj[u]:
                if w not in comp_of:
                    comp_of[w] = comp
                    comp.add(w)
                    queue.append(w)
    return comp_of


def evolution_html(diagrams, steps, case="", variant=""):
    """An ordered gallery: one section per step, file-name order = step order."""
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        "<title>Algorithm 5.1 - step evolution%s</title>" % (
            " - " + case if case else ""),
        "<style>body{font-family:'Segoe UI',Arial,sans-serif;max-width:840px;"
        "margin:24px auto;color:#0f172a}h1{font-size:22px}"
        "h2{font-size:15px;color:#334155;margin:28px 0 6px}"
        ".sub{color:#64748b;font-size:12.5px}svg{border:1px solid #e2e8f0;"
        "border-radius:6px}</style></head><body>",
        "<h1>Algorithm 5.1 - the six steps, one diagram each%s</h1>"
        % (" - case " + _esc(case) if case else ""),
    ]
    if variant:
        parts.append("<p class='sub'>%s</p>" % _esc(variant))
    parts.append("<p class='sub'>Reading order = step order = file-name order "
                 "(step1 ... step6); every diagram uses the same vertex "
                 "layout as the chapter figures, so the six "
                 "pictures form the evolution of one computation.</p>")
    for name in sorted(diagrams):
        first = ""
        if name in steps:
            first = steps[name].splitlines()[0] if steps[name] else ""
        parts.append("<h2>%s</h2>" % _esc(first or name))
        parts.append(diagrams[name])
    parts.append("</body></html>")
    return "\n".join(parts)
