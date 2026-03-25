# 📡 Signal Demodulation Visual Lab

> A fully software-based interactive visualization of **Homodyne** and **Heterodyne** demodulation techniques — applied across Communications, Biomedical, and Mechanical engineering domains.

Built for the **Hackathon Demo** — simulates real-world signal processing pipelines with live interactive dashboards and detailed visualizations.

---

## 🎯 What This Project Does

This lab lets you **see** demodulation happen in real time. You can:

- Watch a signal get modulated, corrupted by noise, and then recovered
- Compare Homodyne vs Heterodyne techniques side by side
- See how the same math applies to ECG heartbeat extraction, bearing fault detection, and radio communications
- Tune live sliders (SNR, carrier frequency, LO offset) and watch recovery quality change instantly

---

## 📂 Project Structure

```
signal_demod_lab/
│
├── requirements.txt              ← all Python dependencies
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
│   └── signal_utils.py           ← shared signal math used by all modules
│
└── outputs/                      ← all PNG plots saved here automatically
```

---

## ⚙️ Setup

### Requirements
- Python 3.8 or higher
- pip

### Step 1 — Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/signal-demod-lab.git
cd signal-demod-lab
```

### Step 2 — Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
pip install dash
```

---

## 🚀 Running the Project

### Option A — Run all static modules at once
```bash
python run_all.py
```
Runs modules 01 through 05 in order. Close each plot window to proceed to the next. All plots are saved automatically to `outputs/`.

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

### Option C — Interactive Dashboard (recommended for demo)
```bash
python 06_interactive_dashboard.py
```
Then open your browser and go to:
```
http://127.0.0.1:8050
```

---

## 📊 Module Breakdown

| Module | What it shows |
|--------|--------------|
| `01_homodyne.py` | Full 4-stage pipeline: message → AM modulation → noise → multiply by LO → low pass filter → recovered signal, shown in both time and frequency domain at every stage |
| `02_heterodyne.py` | Two-stage pipeline showing the carrier being mixed down to an Intermediate Frequency (IF), then filtered to baseband |
| `03_comparison.py` | Both techniques on the same noisy signal, side by side. Includes an SNR sweep graph showing recovery quality from 5 dB to 30 dB |
| `04_biomedical.py` | Synthetic ECG with realistic EMG muscle noise and 50 Hz powerline interference. Also simulates a wireless body-sensor AM demodulation scenario |
| `05_mechanical.py` | Rotating motor bearing simulation with a slowly growing fault. Lock-in amplifier extracts the fault envelope even at SNR = 0 dB |
| `06_interactive_dashboard.py` | Browser-based live dashboard — adjust carrier frequency, noise level, and LO offset with sliders and watch waveforms update in real time |

---

## 🎛️ Interactive Dashboard Controls

| Slider | What it does |
|--------|-------------|
| **Carrier frequency (Hz)** | Changes the frequency of the carrier wave (500–2000 Hz) |
| **Channel SNR (dB)** | Controls how much noise is added. Lower = more noise. 0 dB means noise is as loud as the signal |
| **LO frequency offset (Hz)** | Shifts the local oscillator away from perfect lock. Shows how both techniques degrade when the receiver is not tuned correctly |

The correlation score `r` at the bottom updates live — 1.0 means perfect recovery, anything below 0.8 is poor.

---

## 🔬 Concepts Covered

### Homodyne Demodulation
The receiver uses a local oscillator at **exactly the same frequency** as the carrier. Multiplying the received signal by the LO shifts the message down to baseband. A low-pass filter then removes the high-frequency image. Simple, direct, one step.

### Heterodyne Demodulation
The receiver uses a local oscillator at a **different frequency** from the carrier. This produces an Intermediate Frequency (IF) equal to the difference between the two. A bandpass filter isolates the IF, then a second stage brings it down to baseband. More complex, but more selective and robust against noise.

### Biomedical Application
Bandpass filtering of ECG signals is mathematically equivalent to lock-in demodulation — the filter "tunes into" the cardiac frequency band (0.5–40 Hz) and rejects EMG, motion artefacts, and powerline noise. Used in ECG machines, fMRI signal extraction, and neural recording.

### Mechanical Application
Lock-in amplifiers use homodyne demodulation with a reference signal from a tachometer or shaft encoder. The output is the amplitude and phase of the vibration component that is coherent with the reference — everything else (noise, other harmonics) is rejected. Used in bearing fault detection, MEMS sensors, and non-destructive evaluation (NDE).

---

## 🗂️ Optional — Real ECG Data from PhysioNet

Module `04_biomedical.py` includes commented code to load a real ECG from the MIT-BIH Arrhythmia Database (free, no account needed):

```python
import wfdb
record = wfdb.rdrecord('mitdb/100', sampfrom=0, sampto=5000, pn_dir='mitdb')
real_ecg = record.p_signal[:, 0]
```

Uncomment that section and run with an internet connection to use real clinical data.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| [NumPy](https://numpy.org/) | Signal generation and array math |
| [SciPy](https://scipy.org/) | Digital filters (Butterworth), FFT |
| [Matplotlib](https://matplotlib.org/) | Static time-domain and frequency-domain plots |
| [Plotly](https://plotly.com/) | Interactive charts in the dashboard |
| [Dash](https://dash.plotly.com/) | Browser-based interactive app with sliders |
| [WFDB](https://wfdb.readthedocs.io/) | Loading real biomedical signals from PhysioNet |

---

## 🐛 Troubleshooting

**PowerShell execution policy error on Windows**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Plot window not showing**
```bash
pip install pyqt5
```
Or prefix with: `MPLBACKEND=TkAgg python 01_homodyne.py`

**Port 8050 already in use**
Change the last line of `06_interactive_dashboard.py`:
```python
app.run(debug=False, port=8051)
```

**`outputs/` folder missing**
```bash
mkdir outputs
```
