@echo off
rem One-click run: Algorithm 5.2 (six steps) on every documented case.
rem Data:   uge_data/dataset_uge_<case>/dataset_uge_<case>.txt
rem Output: uge_outs/outs_uge_<case>/  - outs_uge_<case>_step1 ... _step6 reports, their .svg
rem                             diagrams, outs_uge_<case>_evolution.html and
rem                             outs_uge_<case>_result.txt (final gamma'_yz)
setlocal
cd /d "%~dp0"
set "PYTHONPATH=uge_src"
python uge_run.py
endlocal
