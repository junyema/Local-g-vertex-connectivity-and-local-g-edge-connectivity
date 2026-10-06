@echo off
rem One-click run: Algorithm 5.1 (six steps) on every documented case.
rem Data:   ugv_data/dataset_ugv_<case>/dataset_ugv_<case>.txt
rem Output: ugv_outs/outs_ugv_<case>/  - outs_ugv_<case>_step1 ... _step6 reports, their .svg
rem                             diagrams, outs_ugv_<case>_evolution.html and
rem                             outs_ugv_<case>_result.txt (final gamma_yz)
setlocal
cd /d "%~dp0"
set "PYTHONPATH=ugv_src"
python ugv_run.py
endlocal
