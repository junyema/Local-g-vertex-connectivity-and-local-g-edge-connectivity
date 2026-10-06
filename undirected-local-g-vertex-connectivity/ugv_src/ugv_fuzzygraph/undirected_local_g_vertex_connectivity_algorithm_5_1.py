"""Algorithm 5.1 (polynomial six-step algorithm) - master pipeline.

Algorithm 5.1 has exactly six steps; every other algorithm of the chapter
is one of the steps Algorithm 5.1 executes:

  Step 1  LoadGraph      input & validation          (undirected_local_g_vertex_connectivity_step1_load_graph.py)
  Step 2  ClassifyEdges  edge bisection + special    (undirected_local_g_vertex_connectivity_step2_classify_edges.py)
  Step 3  StrongSkeleton drop non-strong edges       (undirected_local_g_vertex_connectivity_step3_strong_skeleton.py)
  Step 4  UnionGraph     distance labels & union     (undirected_local_g_vertex_connectivity_step4_union_graph.py)
  Step 5  OneMinCut      one max-flow                (undirected_local_g_vertex_connectivity_step5_one_min_cut.py)
  Step 6  Finalize       two routes for D & summary  (undirected_local_g_vertex_connectivity_step6_finalize.py)

run_case() executes the six steps on one case file and produces, for every
step, a plain-text report so that each intermediate result can be checked
against the chapter.
"""

import sys
from pathlib import Path

from .undirected_local_g_vertex_connectivity_step1_load_graph import load_graph_file, LoadError
from .undirected_local_g_vertex_connectivity_step2_classify_edges import classify_edges, strong_link_between
from .undirected_local_g_vertex_connectivity_step3_strong_skeleton import strong_skeleton
from .undirected_local_g_vertex_connectivity_step4_union_graph import union_graph
from .undirected_local_g_vertex_connectivity_step5_one_min_cut import weakest_attachment, one_min_cut, INF_CAP
from .undirected_local_g_vertex_connectivity_step6_finalize import finalize, INF
from .undirected_local_g_vertex_connectivity_step_diagrams import Diagrams, evolution_html

EPS = 1e-9

VARIANT = "undirected graph, vertex cuts (Algorithm 5.1)"

# Naming of everything written under ugv_outs/.  A run writes one folder per case,
#     ugv_outs/<OUT_FOLDER_PREFIX><case>/     e.g. ugv_outs/outs_ugv_figure4test/
# and inside it every file is named
#     <OUT_FILE_PREFIX><case>_<report>
# e.g. outs_ugv_figure4test_step1_load_graph.svg
# The folder and the files inside it share the same stem 'outs_<code>_<case>', so
# no folder name and no base name repeats anywhere in the supplement -- the four
# projects each emit their own result.txt / evolution.html / stepN_* reports,
# yet every resulting name stays unique.  The leading 'outs_' marks an output,
# mirroring the 'dataset_' prefix that the input data sets carry.
OUT_PREFIX = "ugv_"

OUT_FILE_PREFIX = "outs_" + OUT_PREFIX

# The case folder repeats the file prefix, so folder name and file name agree.
OUT_FOLDER_PREFIX = OUT_FILE_PREFIX


def _fmt(value):
    if value == INF or value >= 1e10:
        return "+inf"
    return "%g" % value


def _fmt_gamma(gamma):
    t, eta = gamma
    return "(%s, %s)" % (_fmt(t), _fmt(eta))


class CaseResult:
    """Everything Algorithm 5.1 produced for one case, plus the step reports."""

    def __init__(self, case):
        self.case = case
        self.variant = VARIANT
        self.gamma = None
        self.special = False
        self.steps = {}          # report file name -> report text
        self.diagrams = {}       # report file name -> SVG of that step
        self.summary = {}        # key quantities for the console line

    def reports(self):
        """(file name, text) pairs: one report per step, its evolution
        diagram (stepN_*.svg, same order as the steps), the ordered gallery
        evolution.html, and result.txt.  The case name is part of every file
        name, so a base name such as 'result.txt' cannot collide with the same
        report of another case."""
        pfx = OUT_FILE_PREFIX + self.case + "_"
        items = []
        for name in sorted(self.steps):
            items.append((pfx + name + ".txt", self.steps[name]))
        for name in sorted(self.diagrams):
            items.append((pfx + name + ".svg", self.diagrams[name]))
        if self.diagrams:
            items.append((pfx + "evolution.html",
                          evolution_html(self.diagrams, self.steps,
                                         case=self.case, variant=self.variant)))
        items.append((pfx + "result.txt", self._result_text()))
        return items

    def _result_text(self):
        lines = [
            "Algorithm 5.1 - polynomial six-step algorithm (polynomial version)",
            "case    : %s" % self.case,
            "variant : %s" % self.variant,
        ]
        if self.special:
            lines += [
                "route   : special case at the end of Step 2",
                "        (a strong link between y and z exists;",
                "         no vertex cut exists, conventional value)",
                "gamma_yz = %s" % _fmt_gamma(self.gamma),
            ]
        else:
            s = self.summary
            lines += [
                "route   : the six steps of Algorithm 5.1",
                "n, m    : %d vertices, %d edges" % (s["n"], s["m"]),
                "d_F(y,z): %s" % _fmt(s["d"]),
                "t_yz    : %s" % _fmt(s["t"]),
                "S_min   : {%s}" % ", ".join(s["s_min"]),
                "S_max   : {%s}" % ", ".join(s["s_max"]),
                "D1      : %s   (route 1: extreme cuts + two BFS)" % _fmt(s["D1"]),
                "D2      : %s   (route 2: length-cap bisection)" % _fmt(s["D2"]),
                "D       : %s" % _fmt(s["D"]),
                "eta_yz  : %s" % _fmt(self.gamma[1]),
                "gamma_yz = %s" % _fmt_gamma(self.gamma),
            ]
        return "\n".join(lines) + "\n"


def _case_of(path):
    """Case label used in the reports and as the ugv_outs/ folder name: the folder
    name for a per-case folder (ugv_data/<case>/...), the file stem for a loose
    .txt placed directly in ugv_data/.  The 'dataset_<proj>_' prefix -- which keeps
    every data-set name unique in the supplement -- is stripped, so the label
    stays the readable case name (example1, figure4test, ...)."""
    p = Path(path)
    name = p.stem if p.parent.name == "ugv_data" else p.parent.name
    prefix = "dataset_" + OUT_PREFIX
    return name[len(prefix):] if name.startswith(prefix) else name


def run_case(path, eps=EPS):
    """Execute Algorithm 5.1 on the case file `path`; returns a CaseResult."""
    res = CaseResult(_case_of(path))

    # ---- Step 1: LoadGraph -------------------------------------------------
    F, y, z = load_graph_file(path, eps=eps)
    dia = Diagrams(F, y, z, vertex_cut=True)
    res.diagrams["step1_load_graph"] = dia.step1()
    lines = [
        "Step 1 - LoadGraph (input and validation)",
        "endpoint row : y = %s, z = %s" % (y, z),
        "graph        : %d vertices, %d edges, connected" % (F.n(), F.m()),
    ]
    if F.selfloops_dropped:
        lines.append("self-loops dropped at load time: " + ", ".join(
            "%s-%s (%g)" % sl for sl in F.selfloops_dropped))
    else:
        lines.append("self-loops dropped at load time: none")
    lines.append("edges:")
    for (u, v, xi) in F.edge_list():
        lines.append("  %-6s %-6s %g" % (u, v, xi))
    res.steps["step1_load_graph"] = "\n".join(lines) + "\n"

    # ---- Step 2: ClassifyEdges (+ special case) ----------------------------
    strong, weak = classify_edges(F, eps=eps)
    lines = [
        "Step 2 - ClassifyEdges (connectivity strength and edge bisection)",
        "strong edges     : %d" % len(strong),
        "non-strong edges : %d" % len(weak),
    ]
    lines.append("non-strong edge list:")
    for (u, v, xi) in weak:
        lines.append("  %-6s %-6s %g" % (u, v, xi))
    special = strong_link_between(F, y, z, strong)
    if special is not None:
        lines += [
            "special case     : the endpoint edge yz is a STRONG edge,",
            "  no vertex cut exists; Algorithm 5.1 returns the conventional value",
            "  gamma_yz = ((|zeta*| - 1) * xi(y,z), 0) = %s and terminates." % _fmt_gamma(special),
        ]
    else:
        lines.append("special case     : not triggered (y and z are not linked by a strong edge)")
    res.steps["step2_classify_edges"] = "\n".join(lines) + "\n"
    res.diagrams["step2_classify_edges"] = dia.step2(strong, weak, special)

    if special is not None:
        res.special = True
        res.gamma = special
        res.summary = {"n": F.n(), "m": F.m()}
        return res

    # ---- Step 3: StrongSkeleton --------------------------------------------
    Fp = strong_skeleton(F, strong)
    lines = [
        "Step 3 - StrongSkeleton (drop the non-strong edges)",
        "skeleton F'   : %d vertices, %d edges (vertex set unchanged)" % (Fp.n(), Fp.m()),
        "skeleton edges:",
    ]
    for (u, v, xi) in Fp.edge_list():
        lines.append("  %-6s %-6s %g" % (u, v, xi))
    res.steps["step3_strong_skeleton"] = "\n".join(lines) + "\n"
    res.diagrams["step3_strong_skeleton"] = dia.step3(Fp)

    # ---- Step 4: UnionGraph -------------------------------------------------
    d, d_y, d_z, F_yz = union_graph(Fp, y, z)
    lines = [
        "Step 4 - UnionGraph (distance labels and the union graph)",
        "path length is counted in edges (hops); two BFS sweeps, one tight-edge scan",
        "d_F(y, z) = %s" % _fmt(d),
        "distance labels (skeleton vertices):",
        "  %-6s %-6s %-6s" % ("v", "d_y", "d_z"),
    ]
    for v in sorted(Fp.vertices):
        lines.append("  %-6s %-6s %-6s" % (
            v,
            _fmt(d_y[v]) if v in d_y else "inf",
            _fmt(d_z[v]) if v in d_z else "inf",
        ))
    lines += [
        "union graph F_yz : %d vertices, %d edges (tight edges only)" % (F_yz.n(), F_yz.m()),
        "union graph edges:",
    ]
    for (u, v, xi) in F_yz.edge_list():
        lines.append("  %-6s %-6s %g" % (u, v, xi))
    res.steps["step4_union_graph"] = "\n".join(lines) + "\n"
    res.diagrams["step4_union_graph"] = dia.step4(Fp, F_yz, d_y, d_z, d)

    # ---- Step 5: OneMinCut ---------------------------------------------------
    M = weakest_attachment(Fp, F_yz, y, z)
    t_yz, s_min, s_max = one_min_cut(Fp, F_yz, y, z, M)
    lines = [
        "Step 5 - OneMinCut (one max-flow: t_yz and the extreme minimum cuts)",
        "weakest attachment values (split-arc capacities, skeleton minimum):",
        "  %-6s %-10s" % ("v", "M(v)"),
    ]
    for v in sorted(M):
        lines.append("  %-6s %-10s" % (v, _fmt(M[v])))
    lines += [
        "one Dinic max-flow on the split network (source y_out, sink z_in)",
        "t_yz = %s" % _fmt(t_yz),
        "S_min (source side) = {%s}" % ", ".join(s_min),
        "S_max (sink side)   = {%s}" % ", ".join(s_max),
    ]
    res.steps["step5_one_min_cut"] = "\n".join(lines) + "\n"
    res.diagrams["step5_one_min_cut"] = dia.step5(F_yz, t_yz, s_min, s_max)

    # ---- Step 6: Finalize ----------------------------------------------------
    gamma, det = finalize(Fp, d_y, d_z, F_yz, y, z, d, t_yz, s_min, s_max, M,
                          n=F.n(), eps=eps)
    lines = [
        "Step 6 - Finalize (the two routes for D and the summary)",
        "route 1 (extreme minimum cuts + two BFS on F'):",
        "  delete S_min = {%s} -> d = %s" % (", ".join(s_min), _fmt(det["d_min"])),
        "  delete S_max = {%s} -> d = %s" % (", ".join(s_max), _fmt(det["d_max"])),
        "  D1 = %s" % _fmt(det["D1"]),
        "route 2 (length-cap bisection on [%s, %d], one min-cut per probe):" % (
            _fmt(d), F.n() - 1),
        "  %-8s %-12s" % ("probe L", "tau(L)"),
    ]
    for (L, val) in det["probes"]:
        lines.append("  %-8s %-12s" % (L, _fmt(val)))
    lines += [
        "  L* = %s, D2 = L* + 1 = %s" % (_fmt(det["L_star"]), _fmt(det["D2"])),
        "D = max(D1, D2) = %s" % _fmt(det["D"]),
    ]
    if det["D"] == INF:
        lines.append("a fatal cut exists (D = +infinity) -> eta_yz = 1")
    lines += [
        "gamma_yz = (t_yz, 1 - d/D) = %s" % _fmt_gamma(gamma),
        "the two routes agree on D" if det["consistent"] else
        "route 1 (extreme cuts only) is a lower bound here: a middle member of"
        " the lightest family is fatal and route 2 catches it",
    ]
    res.steps["step6_finalize"] = "\n".join(lines) + "\n"
    res.diagrams["step6_finalize"] = dia.step6(Fp, s_min, det, gamma, d)

    res.gamma = gamma
    res.summary = {
        "n": F.n(), "m": F.m(), "d": d, "t": t_yz,
        "s_min": s_min, "s_max": s_max,
        "D1": det["D1"], "D2": det["D2"], "D": det["D"],
    }
    return res


def main(argv):
    """python -m ugv_fuzzygraph.undirected_local_g_vertex_connectivity_algorithm_5_1 FILE  - run Algorithm 5.1 on one case file."""
    if not argv:
        print("usage: python -m ugv_fuzzygraph.undirected_local_g_vertex_connectivity_algorithm_5_1 CASE_FILE")
        return 2
    try:
        res = run_case(argv[0])
    except LoadError as exc:
        print("input rejected by Step 1: %s" % exc)
        return 1
    print(res._result_text())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
