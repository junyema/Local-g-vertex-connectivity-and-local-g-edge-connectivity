"""Run Algorithm 5.2 on every case found in uge_data/ and write reports to uge_outs/.

    python uge_run.py                 # every case found in uge_data/ (auto-discovered)
    python uge_run.py PATH_TO_FILE    # one case file of your own

A case is either a subfolder of uge_data/ named dataset_uge_<case>/ holding the
data set dataset_uge_<case>.txt, or a loose .txt placed directly in uge_data/.
The case name is what follows 'dataset_uge_' in the folder or in the file
name, so uge_data/dataset_uge_example1/dataset_uge_example1.txt is case
'example1'. New cases can be dropped into uge_data/ at any time -- no code
change is needed.

Every case is written to its own folder uge_outs/outs_uge_<case>/, which carries
the same stem as the reports inside it --
outs_uge_<case>_step1_load_graph.txt ... outs_uge_<case>_step6_finalize.txt, the
matching .svg diagrams, outs_uge_<case>_evolution.html and
outs_uge_<case>_result.txt (the final gamma'_yz). The case is part of every name,
so neither a folder name nor a file name repeats in the supplement. EXPECTED
below only re-checks the documented gamma values as a self-check.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "uge_src"))

from uge_fuzzygraph.undirected_local_g_edge_connectivity_algorithm_5_2 import (  # noqa: E402
    run_case, _fmt_gamma, OUT_FOLDER_PREFIX)

# Documented values, used as a self-check.  The keys are the data-set file
# stems (data files are named dataset_uge_<case>.txt); cases without an entry
# here are simply run without the check.
EXPECTED = {
    "dataset_uge_figure6test":  "(0.4, 1)",
    "dataset_uge_figure13test": "(0.6, 0.2)",
    "dataset_uge_figure10test": "(0.6, 1)",
}


def discover_cases():
    """Return the case files under uge_data/: per-case folders and loose .txt."""
    data_dir = HERE / "uge_data"
    paths = []
    if not data_dir.is_dir():
        return paths
    for entry in sorted(data_dir.iterdir()):
        if entry.is_dir():
            exact = entry / (entry.name + ".txt")
            if exact.is_file():
                paths.append(exact)
                continue
            txts = sorted(entry.glob("*.txt"))
            if len(txts) == 1:
                paths.append(txts[0])
            elif len(txts) > 1:
                print("[skip] %s/: several .txt files; name the case file "
                      "after the folder" % entry.name)
        elif entry.suffix.lower() == ".txt":
            paths.append(entry)
    return paths


def write_reports(res, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, text in res.reports():
        (out_dir / name).write_text(text, encoding="utf-8")


def main():
    args = sys.argv[1:]
    if args:
        paths = [Path(p) for p in args]
    else:
        paths = discover_cases()
    out_root = HERE / "uge_outs"

    failures = 0
    for path in paths:
        try:
            res = run_case(path)
        except Exception as exc:  # keep running the remaining cases
            print("[FAIL] %s: %s" % (path, exc))
            failures += 1
            continue
        out_dir = out_root / (OUT_FOLDER_PREFIX + res.case)
        write_reports(res, out_dir)
        gamma = _fmt_gamma(res.gamma)
        note = ""
        want = EXPECTED.get(path.stem)          # keyed by the data-set file name
        if want is not None and gamma != want:
            note = "  (!! documented value is %s)" % want
            failures += 1
        print("[ok] %-12s gamma'_yz = %-18s -> %s%s"
              % (res.case, gamma, out_dir, note))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
