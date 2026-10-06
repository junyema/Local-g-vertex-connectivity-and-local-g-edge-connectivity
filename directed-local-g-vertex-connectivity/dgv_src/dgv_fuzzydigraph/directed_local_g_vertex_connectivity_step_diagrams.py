"""Per-step evolution diagrams for Algorithm 6.1, directed variants (pure SVG).

The diagrams use the FIGURE STYLE OF THE CHAPTER's own figures
the same per-case vertex layout taken from the chapter figures,
arc thickness proportional to xi, light-blue round vertices with a dark-blue
outline, small white weight plates, the chapter's bend-left=18 separation of
opposite arc pairs, red highlights for cuts and the chapter's component
colouring.  The two endpoints y and z sit at the LEFT and RIGHT of the
picture, exactly as in the chapter.

  step1  LoadDigraph     the input fuzzy digraph F (xi written on every arc)
  step2  ClassifyArcs    strong arcs vs non-strong arcs (special case noted)
  step3  StrongSkeleton  the strong skeleton F' (vertex set unchanged)
  step4  UnionGraph      the union digraph F_yz, distance labels d_y / d_z
  step5  OneMinCut       the union digraph F_yz with the minimum cut and t_yz
  step6  Finalize        F' minus the extreme cut S_min, plus gamma_yz

Every method returns an SVG string; directed_local_g_vertex_connectivity_algorithm_6_1.py stores them in
CaseResult.diagrams and run.py writes them next to the step reports, one
`stepN_*.svg` per step plus an ordered `evolution.html` gallery.

The vertex-cut and arc-cut variants share this module: pass
vertex_cut=True for the vertex version (S is a vertex set) and
vertex_cut=False for the arc version (S is an arc set).
"""

import math

from .directed_local_g_vertex_connectivity_step_layouts import lookup

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
_STRONG = "#33566E"                      # rgb 51,86,110 (document strong arc)
_WEAK_DASH = "#9A8FB4"                   # rgb 154,143,180 (document weak arc)
_CUT = "#B20000"                         # red!70!black
_COMP_Y = ("#E4F1E6", "#2E7D4F", "#1B4A30", 1.7)   # green family (reachable from y)
_COMP_Z = ("#FBE4E4", "#C0392B", "#7B1A1A", 1.7)   # red family (can still reach z)
_COMP_BOTH = ("#EDE9FE", "#6B5FA8", "#3D3466", 1.7)  # on a surviving y->z walk
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


def _arc_width(xi):
    """Document convention: arc line width grows linearly with xi."""
    return 0.55 + 2.6 * xi


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


def _unit(p1, p2):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    dist = math.hypot(dx, dy)
    if dist < 1e-9:
        return 0.0, 0.0
    return dx / dist, dy / dist


def _trim(p1, p2, r1, r2):
    ux, uy = _unit(p1, p2)
    return ((p1[0] + ux * r1, p1[1] + uy * r1),
            (p2[0] - ux * r2, p2[1] - uy * r2))


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
    """One diagram per step of Algorithm 6.1, all on the chapter's layout."""

    def __init__(self, F, y, z, vertex_cut=True, case=""):
        self.F = F
        self.y, self.z = y, z
        self.vertex_cut = vertex_cut
        self.keys = set(F.arcs.keys())
        data = lookup(F.vertices)
        if data is not None:
            self.raw = data["pos"]
            self.lab_raw = data["labels"]
            self.bend = set(data.get("bend", {}))
        else:                                    # custom file: circle layout
            self.raw = self._circle_raw(F, y, z)
            self.lab_raw = {}
            self.bend = set()
        self.map, self.scale = _fit(self.raw)
        self.pos = {v: self.map(p) for v, p in self.raw.items()}
        self.labels = {kv: self.map((x, y))
                       for kv, (x, y, _) in self.lab_raw.items()}
        self.vals = {kv: val for kv, (_, _, val) in self.lab_raw.items()}

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
    def _label_pt(self, kv, xi):
        pt = self.labels.get(kv)
        if pt is None:
            (u, v) = kv
            a, b = self.pos[u], self.pos[v]
            pt = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 11)
        return _xi_label(pt, self.vals.get(kv) or _fmt_xi(xi))

    # -- arc drawing ----------------------------------------------------------
    def _draw_arcs(self, styled):
        """styled: [((u, v), xi, color, width, dash)] with arrowheads."""
        parts = []
        for kv, xi, color, width, dash in styled:
            (u, v) = kv
            if kv in self.bend:
                parts.append(self._bend_arc(u, v, color, width, dash))
            else:
                a, b = self.pos[u], self.pos[v]
                ux, uy = _unit(a, b)
                side = -1.0 if (v, u) in self.keys else 0.0   # opposite pair
                if side:
                    a = (a[0] - uy * 3.4 * side, a[1] + ux * 3.4 * side)
                    b = (b[0] - uy * 3.4 * side, b[1] + ux * 3.4 * side)
                parts.append(self._arrow(a, b, color, width, dash))
        for kv, xi, color, width, dash in styled:
            parts.append(self._label_pt(kv, xi))
        return "".join(parts)

    def _arrow(self, a, b, color, width, dash):
        A, B = _trim(a, b, _NODE_R + 2.5, _NODE_R + 6.5)
        C = ((A[0] + B[0]) / 2.0, (A[1] + B[1]) / 2.0)   # collinear midpoint
        return self._arrow_svg(A, C, B, color, width, dash)

    def _bend_arc(self, u, v, color, width, dash):
        """Quadratic arc with the chapter's bend-left=18 side (y-up)."""
        a, b = self.raw[u], self.raw[v]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        cx, cy = mx - dy / L * _SAG * L, my + dx / L * _SAG * L
        A, B, C = self.map(a), self.map(b), self.map((cx, cy))
        A, _t = _trim(A, C, _NODE_R + 2.5, 0)
        B, _t = _trim(B, C, _NODE_R + 6.5, 0)
        return self._arrow_svg(A, C, B, color, width, dash)

    @staticmethod
    def _arrow_svg(A, C, B, color, width, dash):
        """Quadratic A -> (via C) -> B with a triangular head at B."""
        ux, uy = _unit(C, B)
        tip = B
        base = (tip[0] - 9.0 * ux, tip[1] - 9.0 * uy)
        end = (base[0] - 1.0 * ux, base[1] - 1.0 * uy)
        px, py = -uy, ux
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        return ('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
                'stroke="%s" stroke-width="%.2f"%s stroke-linecap="round"/>'
                '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                % (A[0], A[1], C[0], C[1], end[0], end[1], color, width, d,
                   tip[0], tip[1],
                   base[0] + 4.2 * px, base[1] + 4.2 * py,
                   base[0] - 4.2 * px, base[1] - 4.2 * py, color))

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
        loop_txt = ", ".join("%s->%s(%g)" % sl for sl in loops) if loops else "none"
        title = "Step 1 - LoadDigraph: the input fuzzy digraph F"
        sub = ("n = %d vertices, m = %d arcs, y reaches z;  self-loops dropped: %s"
               % (self.F.n(), self.F.m(), loop_txt))
        styled = [(kv, xi, _EDGE, _arc_width(xi), None)
                  for kv, xi in self.F.arcs.items()]
        body = _header(title, sub)
        body += _legend([(_EDGE, None, "arc u -> v, thickness ~ xi")])
        body += '<g>%s</g>' % self._draw_arcs(styled)
        body += '<g>%s</g>' % self._draw_nodes()
        body += _banner([
            "y = %s (left), z = %s (right): the two endpoints of the local"
            % (self.y, self.z),
            "connectivity problem; reachability follows the arc directions.",
        ])
        return _svg_wrap(body)

    # -- Step 2 --------------------------------------------------------------
    def step2(self, strong, weak, special):
        title = "Step 2 - ClassifyArcs: strong vs non-strong arcs"
        sub = ("strong arcs: xi(a) = conn_F(a)  (dark blue)   |   "
               "non-strong arcs: xi(a) < conn_F(a)  (grey dashed)")
        smap = {(u, v): xi for (u, v, xi) in strong}
        styled = []
        for kv, xi in self.F.arcs.items():
            if kv in smap:
                styled.append((kv, xi, _STRONG, 2.5, None))
            else:
                styled.append((kv, xi, _EDGE, _arc_width(xi) * 0.85, "5 3"))
        body = _header(title, sub)
        legend = [(_STRONG, None, "strong")]
        if weak:
            legend.append((_EDGE, "5 3", "non-strong"))
        body += _legend(legend)
        body += '<g>%s</g>' % self._draw_arcs(styled)
        body += '<g>%s</g>' % self._draw_nodes()
        lines = ["strong arcs: %d   non-strong arcs: %d"
                 % (len(strong), len(weak))]
        if special is not None:
            lines += [
                "SPECIAL CASE: the forward arc %s->%s is a STRONG arc;"
                % (self.y, self.z),
                "no vertex cut exists, Algorithm 6.1 returns the conventional",
                "value gamma_yz = ((|zeta*| - 1) * xi(y,z), 0) = %s and stops."
                % _fmt_gamma_pair(special),
            ]
        elif self.vertex_cut:
            lines.append("special case not triggered: no strong forward arc "
                         "%s->%s." % (self.y, self.z))
        else:
            lines.append("no special case in the arc-cut version "
                         "(a direct y->z arc is the trivial lightest cut).")
        body += _banner(lines)
        return _svg_wrap(body)

    # -- Step 3 --------------------------------------------------------------
    def step3(self, Fp):
        title = "Step 3 - StrongSkeleton: drop the non-strong arcs"
        sub = ("skeleton F':  n = %d vertices (UNCHANGED),  m = %d arcs "
               "(strong arcs only)" % (Fp.n(), Fp.m()))
        styled = [(kv, xi, _EDGE, _arc_width(xi), None)
                  for kv, xi in Fp.arcs.items()]
        body = _header(title, sub)
        body += _legend([(_EDGE, None, "strong arc kept in F'")])
        body += '<g>%s</g>' % self._draw_arcs(styled)
        body += '<g>%s</g>' % self._draw_nodes()
        body += _banner([
            "the vertex set does not change; every further step runs on F'.",
        ])
        return _svg_wrap(body)

    # -- Step 4 --------------------------------------------------------------
    def step4(self, Fp, F_yz, d_y, d_z, d):
        title = "Step 4 - UnionGraph: distance labels and tight arcs"
        sub = ("d_F(y,z) = %s hops;  tight arc u->v: d_y(u) + 1 + d_z(v) = "
               "d_F(y,z)" % _fmt_val(d))
        tight = set(F_yz.arcs.keys())
        styled = []
        for kv, xi in Fp.arcs.items():
            if kv in tight:
                styled.append((kv, xi, _EDGE, _arc_width(xi) + 0.5, None))
            else:
                styled.append((kv, xi, _EDGE_FAINT, 1.2, None))
        subs = {}
        for v in Fp.vertices:
            dy = _fmt_val(d_y[v]) if v in d_y else "inf"
            dz = _fmt_val(d_z[v]) if v in d_z else "inf"
            subs[v] = "dy=%s dz=%s" % (dy, dz)
        body = _header(title, sub)
        legend = [(_EDGE, None, "tight arc -> union digraph F_yz")]
        if len(tight) < Fp.m():
            legend.append((_EDGE_FAINT, None, "not on any shortest path"))
        body += _legend(legend)
        body += '<g>%s</g>' % self._draw_arcs(styled)
        body += '<g>%s</g>' % self._draw_nodes(node_sub=subs)
        body += _banner([
            "d_y = hop distances from y along the arcs, d_z = hop distances",
            "that still reach z;  F_yz collects the tight arcs only: "
            "|V| = %d, |A| = %d." % (F_yz.n(), F_yz.m()),
        ])
        return _svg_wrap(body)

    # -- Step 5 --------------------------------------------------------------
    def step5(self, F_yz, t_yz, s_min, s_max):
        t_name = "t_yz" if self.vertex_cut else "t'_yz"
        title = "Step 5 - OneMinCut: %s from ONE max-flow" % t_name
        if self.vertex_cut:
            sub = ("split network with capacities M(v);  source y_out, sink z_in"
                   "  (no arc cut is ever enumerated)")
        else:
            sub = ("every union arc keeps its direction, capacity xi(a);"
                   "  source y, sink z  (no enumeration)")
        cut_keys = self._cut_keys(s_min)
        styled = []
        for kv, xi in F_yz.arcs.items():
            if kv in cut_keys:
                styled.append((kv, xi, _CUT, _arc_width(xi) + 0.6, None))
            else:
                styled.append((kv, xi, _EDGE, _arc_width(xi), None))
        smin_set = set(s_min) if self.vertex_cut else set()
        node_style = {}
        for v in F_yz.vertices:
            if v in smin_set:
                node_style[v] = (_COMP_Z[0], _COMP_Z[1], _COMP_Z[2], 1.8)
        body = _header(title, sub)
        legend = [(_EDGE, None, "union arc"),
                  (_CUT, None, "minimum cut")]
        if self.vertex_cut:
            legend.append((_COMP_Z[1], None, "S_min (source side)"))
        body += _legend(legend)
        body += '<g>%s</g>' % self._draw_arcs(styled)
        body += '<g>%s</g>' % self._draw_nodes(node_style=node_style,
                                               only=set(F_yz.vertices))
        if self.vertex_cut:
            lines = [
                "t_yz = %s" % _fmt_val(t_yz),
                "S_min (source side) = {%s}" % ", ".join(s_min),
                "S_max (sink side)   = {%s}" % ", ".join(s_max),
            ]
        else:
            lines = [
                "t'_yz = %s" % _fmt_val(t_yz),
                "S_min (source side) = %s" % _fmt_arc_cut(s_min),
                "S_max (sink side)   = %s" % _fmt_arc_cut(s_max),
            ]
        body += _banner(lines)
        return _svg_wrap(body)

    def _cut_keys(self, s_min):
        """Arcs crossing the cut, as ordered pairs."""
        if not self.vertex_cut:
            return {(u, v) for (u, v, _) in s_min}
        smin = set(s_min)
        return {(u, v) for (u, v) in self.keys
                if (u in smin) != (v in smin)}

    # -- Step 6 --------------------------------------------------------------
    def step6(self, Fp, s_min, det, gamma, d):
        title = "Step 6 - Finalize: the extreme cut deleted and gamma_yz"
        work = Fp.copy()
        if self.vertex_cut:
            for v in s_min:
                work.remove_vertex(v)
        else:
            for (u, v, _) in s_min:
                work.remove_arc(u, v)
        reach_y = _reach(work, self.y, forward=True)
        reach_z = _reach(work, self.z, forward=False)
        node_style = {}
        for v in work.vertices:
            if v in reach_y and v in reach_z:
                node_style[v] = _COMP_BOTH
            elif v in reach_y:
                node_style[v] = _COMP_Y
            elif v in reach_z:
                node_style[v] = _COMP_Z
            else:
                node_style[v] = _OTHER
        if self.vertex_cut:
            removed_v = set(s_min)
            kept = [kv for kv in Fp.arcs.keys()
                    if kv[0] not in removed_v and kv[1] not in removed_v]
        else:
            cut = {(u, v) for (u, v, _) in s_min}
            kept = [kv for kv in Fp.arcs.keys() if kv not in cut]
        styled = [(kv, Fp.arcs[kv], _EDGE, _arc_width(Fp.arcs[kv]), None)
                  for kv in kept]
        ghosts = []
        if not self.vertex_cut:
            for (u, v, _) in s_min:
                a, b = self.pos[u], self.pos[v]
                ux, uy = _unit(a, b)
                side = -1.0 if (v, u) in self.keys else 0.0
                if side:
                    a = (a[0] - uy * 3.4 * side, a[1] + ux * 3.4 * side)
                    b = (b[0] - uy * 3.4 * side, b[1] + ux * 3.4 * side)
                A, B = _trim(a, b, _NODE_R + 2.5, _NODE_R + 6.5)
                ghosts.append('<path d="M %.1f %.1f L %.1f %.1f" fill="none" '
                              'stroke="%s" stroke-width="1.3" '
                              'stroke-dasharray="4 3"/>'
                              % (A[0], A[1], B[0], B[1], _CUT))
        body = _header(title, "route 1 shown: delete S_min from F' and "
                              "measure the new y-z distance by BFS")
        legend = []
        if reach_y - reach_z:
            legend.append((_COMP_Y[1], None, "reachable from y"))
        if reach_z - reach_y:
            legend.append((_COMP_Z[1], None, "can still reach z"))
        if reach_y & reach_z:
            legend.append((_COMP_BOTH[1], None, "on a surviving y->z walk"))
        if ghosts:
            legend.append((_CUT, "4 3", "deleted by the cut"))
        body += _legend(legend)
        body += '<g>%s</g>' % "".join(ghosts)
        body += '<g>%s</g>' % self._draw_arcs(styled)
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
            lines.append("FATAL: z is no longer reachable from y in F' - S_min"
                         " -> eta = 1")
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


def _fmt_arc_cut(s):
    return "{%s}" % ", ".join("%s->%s(%g)" % (u, v, xi) for (u, v, xi) in s)


def _reach(G, source, forward=True):
    """Vertices reachable from `source` (forward=True) or that can reach it
    (forward=False), following the arc directions."""
    adj = G.out_adj if forward else G.in_adj
    if source not in adj:
        return set()
    seen = {source}
    queue = [source]
    while queue:
        u = queue.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                queue.append(w)
    return seen


def evolution_html(diagrams, steps, case="", variant=""):
    """An ordered gallery: one section per step, file-name order = step order."""
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        "<title>Algorithm 6.1 - step evolution%s</title>" % (
            " - " + case if case else ""),
        "<style>body{font-family:'Segoe UI',Arial,sans-serif;max-width:840px;"
        "margin:24px auto;color:#0f172a}h1{font-size:22px}"
        "h2{font-size:15px;color:#334155;margin:28px 0 6px}"
        ".sub{color:#64748b;font-size:12.5px}svg{border:1px solid #e2e8f0;"
        "border-radius:6px}</style></head><body>",
        "<h1>Algorithm 6.1 - the six steps, one diagram each%s</h1>"
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
