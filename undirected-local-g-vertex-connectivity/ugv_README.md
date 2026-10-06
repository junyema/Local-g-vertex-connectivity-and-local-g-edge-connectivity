# undirected-local-g-vertex-connectivity

Implementation of **Algorithm 5.1** (the polynomial six-step algorithm),
as specified in chapter 5, section on local g-vertex connectivity for
undirected fuzzy graphs.

Algorithm 5.1 has **six steps**; every other algorithm of the chapter is one of
the steps Algorithm 5.1 executes. The `ugv_src/ugv_fuzzygraph/` files are named after those
steps:

| Step | Pseudo-code name | File |
|------|------------------|------|
| 1 | `LoadGraph` | `ugv_src/ugv_fuzzygraph/undirected_local_g_vertex_connectivity_step1_load_graph.py` |
| 2 | `ClassifyEdges` | `ugv_src/ugv_fuzzygraph/undirected_local_g_vertex_connectivity_step2_classify_edges.py` |
| 3 | `StrongSkeleton` | `ugv_src/ugv_fuzzygraph/undirected_local_g_vertex_connectivity_step3_strong_skeleton.py` |
| 4 | `UnionGraph` | `ugv_src/ugv_fuzzygraph/undirected_local_g_vertex_connectivity_step4_union_graph.py` |
| 5 | `OneMinCut` | `ugv_src/ugv_fuzzygraph/undirected_local_g_vertex_connectivity_step5_one_min_cut.py` |
| 6 | `Finalize` | `ugv_src/ugv_fuzzygraph/undirected_local_g_vertex_connectivity_step6_finalize.py` |

`ugv_src/ugv_fuzzygraph/undirected_local_g_vertex_connectivity_algorithm_5_1.py` is the master pipeline of Algorithm 5.1.

## Run

Double-click `ugv_run.bat` (or run it from a console). It executes Algorithm 5.1 on
every case found in `ugv_data/` and writes, for each case, one folder under `ugv_outs/`.
The folder and every file inside it share the same stem `outs_ugv_<case>`, so
neither a folder name nor a file name repeats in the supplement:

    ugv_outs/outs_ugv_<case>/outs_ugv_<case>_step1_load_graph.txt       LoadGraph report (input & validation)
    ugv_outs/outs_ugv_<case>/outs_ugv_<case>_step2_classify_edges.txt   edge bisection report (+ special case)
    ugv_outs/outs_ugv_<case>/outs_ugv_<case>_step3_strong_skeleton.txt  skeleton report
    ugv_outs/outs_ugv_<case>/outs_ugv_<case>_step4_union_graph.txt      distance labels and the union graph
    ugv_outs/outs_ugv_<case>/outs_ugv_<case>_step5_one_min_cut.txt      the one max-flow: t, S_min, S_max
    ugv_outs/outs_ugv_<case>/outs_ugv_<case>_step6_finalize.txt         the two routes for D and the summary
    ugv_outs/outs_ugv_<case>/outs_ugv_<case>_result.txt                 the final pair gamma_yz = (t, eta)

Each step also writes its evolution diagram (`outs_ugv_<case>_stepN_*.svg`); the ordered
gallery of all six diagrams is `outs_ugv_<case>_evolution.html`.

To run one case file of your own:

    python ugv_run.py PATH_TO_FILE

## Cases (data)

The example graphs are stored one folder per case in the project's own `ugv_data/`
directory, with one data-set file per folder:

    ugv_data/dataset_ugv_figure4test/dataset_ugv_figure4test.txt
    ugv_data/dataset_ugv_figure12test/dataset_ugv_figure12test.txt
    ugv_data/dataset_ugv_example1/dataset_ugv_example1.txt
    ugv_data/dataset_ugv_example2/dataset_ugv_example2.txt

**Adding your own cases**: drop a new case into `ugv_data/` and it is picked up
automatically -- no code change needed. Name the data set
`dataset_ugv_<case>.txt` -- the case name is what follows `dataset_ugv_`. Two
layouts are accepted:

    ugv_data/dataset_ugv_mycase/dataset_ugv_mycase.txt   # per-case folder
    ugv_data/dataset_ugv_mycase.txt                      # loose file directly in ugv_data/

Every discovered case is run by `python ugv_run.py` (or `ugv_run.bat`) and gets its
own folder under `ugv_outs/`. A folder holding several .txt files is skipped;
cases without an entry in `EXPECTED` (see ugv_run.py) run without the
documented-value self-check. Alternatively run one file directly:
`python ugv_run.py PATH_TO_FILE`.

## Dependencies

None beyond the Python standard library (the max-flow is a small built-in
Dinic implementation).
