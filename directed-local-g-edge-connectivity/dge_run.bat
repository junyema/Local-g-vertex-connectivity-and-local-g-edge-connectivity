@echo off
rem One-click run: Algorithm 6.2 (six steps) on every documented case.
rem Data:   dge_data/dataset_dge_<case>/dataset_dge_<case>.txt
rem Output: dge_outs/outs_dge_<case>/  - outs_dge_<case>_step1 ... _step6 reports, their .svg
rem                             diagrams, outs_dge_<case>_evolution.html and
rem                             outs_dge_<case>_result.txt (final gamma'_yz)
setlocal
cd /d "%~dp0"
set "PYTHONPATH=dge_src"
python dge_run.py
endlocal
