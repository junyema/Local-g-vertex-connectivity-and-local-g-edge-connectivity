# undirected-local-g-edge-connectivity

Implementation of **Algorithm 5.2** (the polynomial six-step algorithm)
as specified in chapter 5, section on local g-edge connectivity for
undirected fuzzy graphs.

Algorithm 5.2 has **six steps**; every other algorithm of the chapter is one of
the steps Algorithm 5.2 executes. The `uge_src/uge_fuzzygraph/` files are named after those
steps:

| Step | Pseudo-code name | File |
|------|------------------|------|
| 1 | `LoadGraph` | `uge_src/uge_fuzzygraph/undirected_local_g_edge_connectivity_step1_load_graph.py` |
| 2 | `ClassifyEdges` | `uge_src/uge_fuzzygraph/undirected_local_g_edge_connectivity_step2_classify_edges.py` |
| 3 | `StrongSkeleton` | `uge_src/uge_fuzzygraph/undirected_local_g_edge_connectivity_step3_strong_skeleton.py` |
| 4 | `UnionGraph` | `uge_src/uge_fuzzygraph/undirected_local_g_edge_connectivity_step4_union_graph.py` |
| 5 | `OneMinCut` | `uge_src/uge_fuzzygraph/undirected_local_g_edge_connectivity_step5_one_min_cut.py` |
| 6 | `Finalize` | `uge_src/uge_fuzzygraph/undirected_local_g_edge_connectivity_step6_finalize.py` |

`uge_src/uge_fuzzygraph/undirected_local_g_edge_connectivity_algorithm_5_2.py` is the master pipeline of Algorithm 5.2.

## Run

Double-click `uge_run.bat` (or run it from a console). It executes Algorithm 5.2 on
every case found in `uge_data/` and writes, for each case, one folder under `uge_outs/`.
The folder and every file inside it share the same stem `outs_uge_<case>`, so
neither a folder name nor a file name repeats in the supplement:

    uge_outs/outs_uge_<case>/outs_uge_<case>_step1_load_graph.txt       LoadGraph report (input & validation)
    uge_outs/outs_uge_<case>/outs_uge_<case>_step2_classify_edges.txt   edge bisection report (+ special case)
    uge_outs/outs_uge_<case>/outs_uge_<case>_step3_strong_skeleton.txt  skeleton report
    uge_outs/outs_uge_<case>/outs_uge_<case>_step4_union_graph.txt      distance labels and the union graph
    uge_outs/outs_uge_<case>/outs_uge_<case>_step5_one_min_cut.txt      the one max-flow: t', S_min, S_max
    uge_outs/outs_uge_<case>/outs_uge_<case>_step6_finalize.txt         the two routes for D and the summary
    uge_outs/outs_uge_<case>/outs_uge_<case>_result.txt                 the final pair gamma'_yz = (t', eta)

Each step also writes its evolution diagram (`outs_uge_<case>_stepN_*.svg`); the ordered
gallery of all six diagrams is `outs_uge_<case>_evolution.html`.

To run one case file of your own:

    python uge_run.py PATH_TO_FILE

## Cases (data)

The example graphs are stored one folder per case in the project's own `uge_data/`
directory, with one data-set file per folder:

    uge_data/dataset_uge_figure6test/dataset_uge_figure6test.txt
    uge_data/dataset_uge_figure13test/dataset_uge_figure13test.txt
    uge_data/dataset_uge_figure10test/dataset_uge_figure10test.txt
    uge_data/dataset_uge_example1/dataset_uge_example1.txt
    uge_data/dataset_uge_example2/dataset_uge_example2.txt

**Adding your own cases**: drop a new case into `uge_data/` and it is picked up
automatically -- no code change needed. Name the data set
`dataset_uge_<case>.txt` -- the case name is what follows `dataset_uge_`. Two
layouts are accepted:

    uge_data/dataset_uge_mycase/dataset_uge_mycase.txt   # per-case folder
    uge_data/dataset_uge_mycase.txt                      # loose file directly in uge_data/

Every discovered case is run by `python uge_run.py` (or `uge_run.bat`) and gets its
own folder under `uge_outs/`. A folder holding several .txt files is skipped;
cases without an entry in `EXPECTED` (see uge_run.py) run without the
documented-value self-check. Alternatively run one file directly:
`python uge_run.py PATH_TO_FILE`.

## Dependencies

None beyond the Python standard library (the max-flow is a small built-in
Dinic implementation).
