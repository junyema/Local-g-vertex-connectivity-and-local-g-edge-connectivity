# directed-local-g-edge-connectivity

Implementation of **Algorithm 6.2** (the polynomial six-step algorithm)
as specified in chapter 6, section on local g-edge connectivity for
directed fuzzy graphs.

Algorithm 6.2 has **six steps**; every other algorithm of the chapter is one of
the steps Algorithm 6.2 executes. The `dge_src/dge_fuzzydigraph/` files are named after those
steps:

| Step | Pseudo-code name | File |
|------|------------------|------|
| 1 | `LoadDigraph` | `dge_src/dge_fuzzydigraph/directed_local_g_edge_connectivity_step1_load_digraph.py` |
| 2 | `ClassifyArcs` | `dge_src/dge_fuzzydigraph/directed_local_g_edge_connectivity_step2_classify_arcs.py` |
| 3 | `StrongSkeleton` | `dge_src/dge_fuzzydigraph/directed_local_g_edge_connectivity_step3_strong_skeleton.py` |
| 4 | `UnionGraph` | `dge_src/dge_fuzzydigraph/directed_local_g_edge_connectivity_step4_union_graph.py` |
| 5 | `OneMinCut` | `dge_src/dge_fuzzydigraph/directed_local_g_edge_connectivity_step5_one_min_cut.py` |
| 6 | `Finalize` | `dge_src/dge_fuzzydigraph/directed_local_g_edge_connectivity_step6_finalize.py` |

`dge_src/dge_fuzzydigraph/directed_local_g_edge_connectivity_algorithm_6_2.py` is the master pipeline of Algorithm 6.2.

## Run

Double-click `dge_run.bat` (or run it from a console). It executes Algorithm 6.2 on
every case found in `dge_data/` and writes, for each case, one folder under `dge_outs/`.
The folder and every file inside it share the same stem `outs_dge_<case>`, so
neither a folder name nor a file name repeats in the supplement:

    dge_outs/outs_dge_<case>/outs_dge_<case>_step1_load_digraph.txt     LoadDigraph report (input & validation)
    dge_outs/outs_dge_<case>/outs_dge_<case>_step2_classify_arcs.txt    arc bisection report (+ special case)
    dge_outs/outs_dge_<case>/outs_dge_<case>_step3_strong_skeleton.txt  skeleton report
    dge_outs/outs_dge_<case>/outs_dge_<case>_step4_union_graph.txt      distance labels and the union graph
    dge_outs/outs_dge_<case>/outs_dge_<case>_step5_one_min_cut.txt      the one max-flow: t', S_min, S_max
    dge_outs/outs_dge_<case>/outs_dge_<case>_step6_finalize.txt         the two routes for D and the summary
    dge_outs/outs_dge_<case>/outs_dge_<case>_result.txt                 the final pair gamma'_yz = (t', eta)

Each step also writes its evolution diagram (`outs_dge_<case>_stepN_*.svg`); the ordered
gallery of all six diagrams is `outs_dge_<case>_evolution.html`.

To run one case file of your own:

    python dge_run.py PATH_TO_FILE

## Cases (data)

The example graphs are stored one folder per case in the project's own `dge_data/`
directory, with one data-set file per folder:

    dge_data/dataset_dge_advogatotest/dataset_dge_advogatotest.txt
    dge_data/dataset_dge_figure8test/dataset_dge_figure8test.txt
    dge_data/dataset_dge_figure14test/dataset_dge_figure14test.txt
    dge_data/dataset_dge_figure11test/dataset_dge_figure11test.txt
    dge_data/dataset_dge_example3/dataset_dge_example3.txt

**Adding your own cases**: drop a new case into `dge_data/` and it is picked up
automatically -- no code change needed. Name the data set
`dataset_dge_<case>.txt` -- the case name is what follows `dataset_dge_`. Two
layouts are accepted:

    dge_data/dataset_dge_mycase/dataset_dge_mycase.txt   # per-case folder
    dge_data/dataset_dge_mycase.txt                      # loose file directly in dge_data/

Every discovered case is run by `python dge_run.py` (or `dge_run.bat`) and gets its
own folder under `dge_outs/`. A folder holding several .txt files is skipped;
cases without an entry in `EXPECTED` (see dge_run.py) run without the
documented-value self-check. Alternatively run one file directly:
`python dge_run.py PATH_TO_FILE`.

## Dependencies

None beyond the Python standard library (the max-flow is a small built-in
Dinic implementation).
