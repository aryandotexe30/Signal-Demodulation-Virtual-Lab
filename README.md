# Signal Demodulation Visual Lab
### Hackathon Demo — Homodyne & Heterodyne Demodulation
---

## Project Structure

```
signal_demod_lab/
│
├── requirements.txt              ← install all dependencies from here
├── run_all.py                    ← runs every module in sequence
│
├── 01_homodyne.py                ← Homodyne demodulation pipeline
├── 02_heterodyne.py              ← Heterodyne two-stage pipeline
├── 03_comparison.py              ← Side-by-side comparison + SNR sweep
├── 04_biomedical.py              ← ECG signal processing (biomedical)
├── 05_mechanical.py              ← Lock-in amplifier / bearing fault (mechanical)
├── 06_interactive_dashboard.py   ← Interactive Plotly/Dash browser app
│
├── utils/
│   ├── __init__.py
│   └── signal_utils.py           ← shared signal math (used by all modules)
│
└── outputs/                      ← PNG plots saved here automatically
```

---

## Setup Instructions (do this ONCE)

### Step 1 — Make sure Python is installed
Open a terminal (VSCode Terminal: Ctrl+` ) and run:
```
python --version
```
You need Python 3.8 or higher.  If not installed: https://www.python.org/downloads/

---

### Step 2 — Open the project folder in VSCode
```
File → Open Folder → select the signal_demod_lab folder
```

---

### Step 3 — Create a virtual environment (recommended)
In the VSCode terminal:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```
You should see `(venv)` appear in your terminal prompt.

---

### Step 4 — Install all dependencies
```bash
pip install -r requirements.txt
```
Also install Dash (for the interactive module):
```bash
pip install dash
```

This installs: numpy, scipy, matplotlib, plotly, dash, wfdb

---

## Running the Modules

### Option A — Run everything at once
```bash
python run_all.py
```
This runs modules 01 through 05 in order.
Each opens a plot window.  **Close the window** to move to the next module.
All plots are saved automatically to `outputs/`.

---

### Option B — Run individual modules
```bash
python 01_homodyne.py
python 02_heterodyne.py
python 03_comparison.py
python 04_biomedical.py
python 05_mechanical.py
```

---

### Option C — Interactive Dashboard (best for demo video)
```bash
python 06_interactive_dashboard.py
```
Then open your browser and go to:
```
http://127.0.0.1:8050
```
You'll see a live dashboard with sliders for:
- Carrier frequency
- SNR (noise level)
- LO frequency offset (shows how homodyne breaks when not phase-locked)

Press `Ctrl+C` in the terminal to stop the server.

---

## What Each Module Shows

| File | Topic |
|------|-------|
| `01_homodyne.py` | Full 4-stage pipeline: message → AM → noise → ×LO → LPF → recovered |
| `02_heterodyne.py` | Two-stage pipeline: carrier → IF stage → baseband |
| `03_comparison.py` | Side-by-side + SNR sweep: how both perform across noise levels |
| `04_biomedical.py` | Synthetic ECG with EMG/powerline noise, AM wireless ECG scenario |
| `05_mechanical.py` | Rotating machinery fault detection via lock-in at SNR = 0 dB |
| `06_interactive_dashboard.py` | Browser-based live sliders — best for demo recording |

---

## Demo Video Workflow

1. Start screen recording (OBS Studio or Windows Game Bar: Win+G)
2. Open VSCode with this folder
3. Run `python 06_interactive_dashboard.py` in terminal
4. Open `http://127.0.0.1:8050` in browser
5. Walk through the sliders — narrate what each does
6. Switch to VSCode and run `python 03_comparison.py` to show the static comparison
7. Run `python 04_biomedical.py` — explain the ECG scenario
8. Run `python 05_mechanical.py` — explain the bearing fault scenario
9. Stop recording

Total runtime: ~5 minutes

---

## Optional: Real ECG Data from PhysioNet

Module 04 includes commented code to load real ECG data.
Uncomment it and run with internet connection:
```python
import wfdb
record = wfdb.rdrecord('mitdb/100', sampfrom=0, sampto=5000, pn_dir='mitdb')
```
This downloads from https://physionet.org — free, no account needed.

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'dash'`**
→ Run: `pip install dash`

**Plot window is blank / not showing**
→ On some systems, use: `MPLBACKEND=TkAgg python 01_homodyne.py`

**`outputs/` folder not found error**
→ Create it manually: `mkdir outputs`

**Port 8050 already in use**
→ Change line in `06_interactive_dashboard.py`: `app.run(debug=False, port=8051)`
