"""
MODULE 1 — Homodyne Demodulation
=================================
Concept: The local oscillator (LO) runs at EXACTLY the same frequency
as the carrier.  Multiplying the received signal by the LO shifts the
message down to baseband.  A low-pass filter then cleans it up.

Pipeline:
  Message (10 Hz)
      │
  AM Modulator  ←── Carrier (1 kHz)
      │
  AWGN Channel (SNR = 20 dB)
      │
  × LO  (1 kHz — same frequency)
      │
  Low-Pass Filter (cutoff = 50 Hz)
      │
  Recovered message

Run:  python 01_homodyne.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from utils.signal_utils import (
    make_time, sine, am_modulate, add_noise,
    lowpass, compute_spectrum
)

# ── Parameters ─────────────────────────────────────────────────────────────────
FS          = 10_000   # sample rate (Hz)
DURATION    = 1.0      # seconds
FC          = 1_000    # carrier frequency (Hz)
FM          = 10       # message frequency (Hz)
MOD_INDEX   = 0.8      # AM modulation depth
SNR_DB      = 20       # channel noise level
LPF_CUTOFF  = 50       # low-pass filter cutoff (Hz)

# ── Generate signals ────────────────────────────────────────────────────────────
t, fs = make_time(DURATION, FS)

message        = sine(t, FM)
modulated      = am_modulate(FC, message, t, MOD_INDEX)
received       = add_noise(modulated, SNR_DB)

# ── Homodyne demodulation ───────────────────────────────────────────────────────
lo             = np.cos(2 * np.pi * FC * t)          # LO at SAME freq as carrier
mixed          = received * lo                        # multiply (down-convert)
recovered      = lowpass(mixed, LPF_CUTOFF, FS)       # low-pass filter

# Normalise amplitude (the multiply introduces a 0.5 factor)
recovered     *= 2

# ── Compute spectra ─────────────────────────────────────────────────────────────
f_mod, S_mod   = compute_spectrum(modulated, FS)
f_rcv, S_rcv   = compute_spectrum(received,  FS)
f_mix, S_mix   = compute_spectrum(mixed,     FS)
f_rec, S_rec   = compute_spectrum(recovered, FS)

# ── Plot ────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 10))
fig.suptitle("Homodyne Demodulation — Complete Pipeline", fontsize=14, fontweight='bold')

gs = gridspec.GridSpec(4, 2, figure=fig, hspace=0.55, wspace=0.35)

SHOW = slice(0, int(FS * 0.05))   # show first 50 ms for clarity

def plot_row(ax_t, ax_f, sig, freqs, spec, row_label, color,
             t_arr=t, f_max=2200):
    ax_t.plot(t_arr[SHOW] * 1000, sig[SHOW], color=color, lw=0.9)
    ax_t.set_ylabel("Amplitude", fontsize=8)
    ax_t.set_xlabel("Time (ms)", fontsize=8)
    ax_t.set_title(row_label + " — Time domain", fontsize=9)
    ax_t.tick_params(labelsize=7)
    ax_t.grid(True, alpha=0.3)

    mask = freqs <= f_max
    ax_f.plot(freqs[mask], spec[mask], color=color, lw=0.9)
    ax_f.set_ylabel("|Magnitude|", fontsize=8)
    ax_f.set_xlabel("Frequency (Hz)", fontsize=8)
    ax_f.set_title(row_label + " — Frequency domain", fontsize=9)
    ax_f.tick_params(labelsize=7)
    ax_f.grid(True, alpha=0.3)

# Row 0 — original message
ax00 = fig.add_subplot(gs[0, 0])
ax01 = fig.add_subplot(gs[0, 1])
plot_row(ax00, ax01, message, *compute_spectrum(message, FS),
         "① Original message (10 Hz)", "#1d9e75")

# Row 1 — modulated + noisy received
ax10 = fig.add_subplot(gs[1, 0])
ax11 = fig.add_subplot(gs[1, 1])
plot_row(ax10, ax11, received, f_rcv, S_rcv,
         "② Received signal (AM + noise)", "#e07b3f")

# Row 2 — after multiply with LO
ax20 = fig.add_subplot(gs[2, 0])
ax21 = fig.add_subplot(gs[2, 1])
plot_row(ax20, ax21, mixed, f_mix, S_mix,
         "③ After × LO — baseband + 2fc image", "#7f77dd")

# Row 3 — recovered
ax30 = fig.add_subplot(gs[3, 0])
ax31 = fig.add_subplot(gs[3, 1])
plot_row(ax30, ax31, recovered, f_rec, S_rec,
         "④ Recovered message (after LPF)", "#d85a30", f_max=200)

# Annotate frequency-domain panels
ax11.axvline(FC, color='red', lw=0.8, ls='--', label=f'fc = {FC} Hz')
ax11.legend(fontsize=7)
ax21.axvline(0,      color='green', lw=0.8, ls='--', label='Baseband')
ax21.axvline(2*FC,   color='red',   lw=0.8, ls='--', label='2fc image')
ax21.legend(fontsize=7)

plt.savefig("outputs/01_homodyne.png", dpi=150, bbox_inches='tight')
print("✓ Saved  outputs/01_homodyne.png")
plt.show()
