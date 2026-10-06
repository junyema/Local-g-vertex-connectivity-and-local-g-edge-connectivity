@echo off
rem One-click run: Algorithm 6.1 (six steps) on every documented case.
rem Data:   dgv_data/dataset_dgv_<case>/dataset_dgv_<case>.txt
rem Output: dgv_outs/outs_dgv_<case>/  - outs_dgv_<case>_step1 ... _step6 reports, their .svg
rem                             diagrams, outs_dgv_<case>_evolution.html and
rem                             outs_dgv_<case>_result.txt (final gamma_yz)
setlocal
cd /d "%~dp0"
set "PYTHONPATH=dgv_src"
python dgv_run.py
endlocal
