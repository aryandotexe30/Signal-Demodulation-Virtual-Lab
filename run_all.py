"""
RUN ALL — executes all static visualization modules in sequence.
Each one saves a PNG to outputs/ and displays its plot window.
Close each plot window to proceed to the next module.

Usage:  python run_all.py
"""

import subprocess
import sys

modules = [
    ("01_homodyne.py",       "Homodyne Demodulation"),
    ("02_heterodyne.py",     "Heterodyne Demodulation"),
    ("03_comparison.py",     "Homodyne vs Heterodyne Comparison"),
    ("04_biomedical.py",     "Biomedical — ECG"),
    ("05_mechanical.py",     "Mechanical — Bearing Fault / Lock-in"),
]

print("\n" + "═"*55)
print("  SIGNAL DEMODULATION VISUAL LAB")
print("  Running all modules...")
print("═"*55 + "\n")

for script, label in modules:
    print(f"▶  {label}")
    print(f"   Running {script} ...")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"   ✗  {script} failed — check errors above")
    else:
        print(f"   ✓  Done\n")

print("═"*55)
print("  All modules complete.  Check outputs/ folder.")
print("═"*55)
print()
print("  For interactive dashboard, run:")
print("  python 06_interactive_dashboard.py")
print("  Then open  http://127.0.0.1:8050")
print()
