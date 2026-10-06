# directed-local-g-vertex-connectivity

Implementation of **Algorithm 6.1** (the polynomial six-step algorithm)
as specified in chapter 6, section on local g-vertex connectivity for
directed fuzzy graphs.

Algorithm 6.1 has **six steps**; every other algorithm of the chapter is one of
the steps Algorithm 6.1 executes. The `dgv_src/dgv_fuzzydigraph/` files are named after those
steps:

| Step | Pseudo-code name | File |
|------|------------------|------|
| 1 | `LoadDigraph` | `dgv_src/dgv_fuzzydigraph/directed_local_g_vertex_connectivity_step1_load_digraph.py` |
| 2 | `ClassifyArcs` | `dgv_src/dgv_fuzzydigraph/directed_local_g_vertex_connectivity_step2_classify_arcs.py` |
| 3 | `StrongSkeleton` | `dgv_src/dgv_fuzzydigraph/directed_local_g_vertex_connectivity_step3_strong_skeleton.py` |
| 4 | `UnionGraph` | `dgv_src/dgv_fuzzydigraph/directed_local_g_vertex_connectivity_step4_union_graph.py` |
| 5 | `OneMinCut` | `dgv_src/dgv_fuzzydigraph/directed_local_g_vertex_connectivity_step5_one_min_cut.py` |
| 6 | `Finalize` | `dgv_src/dgv_fuzzydigraph/directed_local_g_vertex_connectivity_step6_finalize.py` |

`dgv_src/dgv_fuzzydigraph/directed_local_g_vertex_connectivity_algorithm_6_1.py` is the master pipeline of Algorithm 6.1.

## Run

Double-click `dgv_run.bat` (or run it from a console). It executes Algorithm 6.1 on
every case found in `dgv_data/` and writes, for each case, one folder under `dgv_outs/`.
The folder and every file inside it share the same stem `outs_dgv_<case>`, so
neither a folder name nor a file name repeats in the supplement:

    dgv_outs/outs_dgv_<case>/outs_dgv_<case>_step1_load_digraph.txt     LoadDigraph report (input & validation)
    dgv_outs/outs_dgv_<case>/outs_dgv_<case>_step2_classify_arcs.txt    arc bisection report (+ special case)
    dgv_outs/outs_dgv_<case>/outs_dgv_<case>_step3_strong_skeleton.txt  skeleton report
    dgv_outs/outs_dgv_<case>/outs_dgv_<case>_step4_union_graph.txt      distance labels and the union graph
    dgv_outs/outs_dgv_<case>/outs_dgv_<case>_step5_one_min_cut.txt      the one max-flow: t, S_min, S_max
    dgv_outs/outs_dgv_<case>/outs_dgv_<case>_step6_finalize.txt         the two routes for D and the summary
    dgv_outs/outs_dgv_<case>/outs_dgv_<case>_result.txt                 the final pair gamma_yz = (t, eta)

Each step also writes its evolution diagram (`outs_dgv_<case>_stepN_*.svg`); the ordered
gallery of all six diagrams is `outs_dgv_<case>_evolution.html`.

To run one case file of your own:

    python dgv_run.py PATH_TO_FILE

## Cases (data)

The example graphs are stored one folder per case in the project's own `dgv_data/`
directory, with one data-set file per folder:

    dgv_data/dataset_dgv_advogatotest/dataset_dgv_advogatotest.txt
    dgv_data/dataset_dgv_figure8test/dataset_dgv_figure8test.txt
    dgv_data/dataset_dgv_figure14test/dataset_dgv_figure14test.txt
    dgv_data/dataset_dgv_figure11test/dataset_dgv_figure11test.txt
    dgv_data/dataset_dgv_example3/dataset_dgv_example3.txt

**Adding your own cases**: drop a new case into `dgv_data/` and it is picked up
automatically -- no code change needed. Name the data set
`dataset_dgv_<case>.txt` -- the case name is what follows `dataset_dgv_`. Two
layouts are accepted:

    dgv_data/dataset_dgv_mycase/dataset_dgv_mycase.txt   # per-case folder
    dgv_data/dataset_dgv_mycase.txt                      # loose file directly in dgv_data/

Every discovered case is run by `python dgv_run.py` (or `dgv_run.bat`) and gets its
own folder under `dgv_outs/`. A folder holding several .txt files is skipped;
cases without an entry in `EXPECTED` (see dgv_run.py) run without the
documented-value self-check. Alternatively run one file directly:
`python dgv_run.py PATH_TO_FILE`.

## Dependencies

None beyond the Python standard library (the max-flow is a small built-in
Dinic implementation).
