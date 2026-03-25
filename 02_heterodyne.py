"""
MODULE 2 — Heterodyne Demodulation
====================================
Concept: The LO runs at a DIFFERENT frequency from the carrier.
Mixing produces an Intermediate Frequency (IF) = |fc - f_LO|.
A bandpass filter isolates the IF, then a second demodulation
stage brings it down to baseband.

Pipeline:
  Message (10 Hz)
      │
  AM Modulator  ←── Carrier (1 kHz)
      │
  AWGN Channel (SNR = 20 dB)
      │
  × LO  (1.1 kHz — different frequency)
      │
  IF = 100 Hz  →  Bandpass Filter (80–120 Hz)
      │
  × Second LO (100 Hz)
      │
  Low-Pass Filter (cutoff = 30 Hz)
      │
  Recovered message

Run:  python 02_heterodyne.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from utils.signal_utils import (
    make_time, sine, am_modulate, add_noise,
    lowpass, bandpass, compute_spectrum
)

# ── Parameters ─────────────────────────────────────────────────────────────────
FS          = 10_000
DURATION    = 1.0
FC          = 1_000    # carrier (Hz)
FM          = 10       # message (Hz)
F_LO1       = 1_100    # first LO — DIFFERENT from carrier
F_IF        = abs(FC - F_LO1)   # = 100 Hz
F_LO2       = F_IF     # second LO at IF freq
SNR_DB      = 20
LPF_CUTOFF  = 30

# ── Generate signals ────────────────────────────────────────────────────────────
t, fs = make_time(DURATION, FS)

message        = sine(t, FM)
modulated      = am_modulate(FC, message, t, mod_index=0.8)
received       = add_noise(modulated, SNR_DB)

# ── Stage 1: Down-convert to IF ─────────────────────────────────────────────────
lo1            = np.cos(2 * np.pi * F_LO1 * t)
after_mix1     = received * lo1
if_signal      = bandpass(after_mix1, F_IF - 20, F_IF + 20, FS)   # isolate IF band

# ── Stage 2: Down-convert IF to baseband ────────────────────────────────────────
lo2            = np.cos(2 * np.pi * F_LO2 * t)
after_mix2     = if_signal * lo2
recovered      = lowpass(after_mix2, LPF_CUTOFF, FS)
recovered     *= 2   # amplitude correction

# ── Spectra ─────────────────────────────────────────────────────────────────────
f_rcv, S_rcv   = compute_spectrum(received,    FS)
f_mix1, S_mix1 = compute_spectrum(after_mix1,  FS)
f_if,  S_if    = compute_spectrum(if_signal,   FS)
f_mix2, S_mix2 = compute_spectrum(after_mix2,  FS)
f_rec, S_rec   = compute_spectrum(recovered,   FS)

# ── Plot ────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 12))
fig.suptitle("Heterodyne Demodulation — Two-Stage Pipeline", fontsize=14, fontweight='bold')

gs = gridspec.GridSpec(5, 2, figure=fig, hspace=0.6, wspace=0.35)
SHOW = slice(0, int(FS * 0.05))

rows = [
    (received,    f_rcv,  S_rcv,  "① Received signal",                   "#e07b3f", 2200),
    (after_mix1,  f_mix1, S_mix1, "② After × LO1 (1.1 kHz)",            "#7f77dd", 2500),
    (if_signal,   f_if,   S_if,   f"③ IF signal ({F_IF} Hz) after BPF",  "#1d9e75", 500),
    (after_mix2,  f_mix2, S_mix2, "④ After × LO2 (100 Hz)",              "#d4537e", 400),
    (recovered,   f_rec,  S_rec,  "⑤ Recovered message (after LPF)",     "#185fa5", 100),
]

for i, (sig, freqs, spec, label, color, fmax) in enumerate(rows):
    ax_t = fig.add_subplot(gs[i, 0])
    ax_f = fig.add_subplot(gs[i, 1])
    ax_t.plot(t[SHOW]*1000, sig[SHOW], color=color, lw=0.9)
    ax_t.set_title(label + " — Time", fontsize=9)
    ax_t.set_xlabel("Time (ms)", fontsize=8)
    ax_t.set_ylabel("Amplitude", fontsize=8)
    ax_t.tick_params(labelsize=7)
    ax_t.grid(True, alpha=0.3)

    mask = freqs <= fmax
    ax_f.plot(freqs[mask], spec[mask], color=color, lw=0.9)
    ax_f.set_title(label + " — Spectrum", fontsize=9)
    ax_f.set_xlabel("Frequency (Hz)", fontsize=8)
    ax_f.set_ylabel("|Magnitude|", fontsize=8)
    ax_f.tick_params(labelsize=7)
    ax_f.grid(True, alpha=0.3)

# Mark IF on stage-2 spectrum
fig.axes[3].axvline(F_IF, color='green', ls='--', lw=0.9, label=f'IF = {F_IF} Hz')
fig.axes[3].legend(fontsize=7)

plt.savefig("outputs/02_heterodyne.png", dpi=150, bbox_inches='tight')
print("✓ Saved  outputs/02_heterodyne.png")
plt.show()
