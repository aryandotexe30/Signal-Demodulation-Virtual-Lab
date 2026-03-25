"""
MODULE 3 — Homodyne vs Heterodyne Comparison
=============================================
Side-by-side visual comparison of both techniques on the
same input signal.  Also sweeps SNR from 5 dB to 30 dB
and plots recovery quality (correlation with original).

Run:  python 03_comparison.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import pearsonr
from utils.signal_utils import (
    make_time, sine, am_modulate, add_noise,
    lowpass, bandpass, compute_spectrum
)

FS, DURATION = 10_000, 1.0
FC, FM       = 1_000, 10
F_LO1        = 1_100
F_IF         = abs(FC - F_LO1)

t, fs = make_time(DURATION, FS)
SHOW  = slice(0, int(FS * 0.08))


def homodyne(received, t, fc=FC, lpf=50):
    lo  = np.cos(2 * np.pi * fc * t)
    out = lowpass(received * lo, lpf, FS)
    return out * 2


def heterodyne(received, t, f_lo1=F_LO1, f_if=F_IF, lpf=30):
    lo1   = np.cos(2 * np.pi * f_lo1 * t)
    stage1 = bandpass(received * lo1, f_if - 20, f_if + 20, FS)
    lo2   = np.cos(2 * np.pi * f_if * t)
    out   = lowpass(stage1 * lo2, lpf, FS)
    return out * 2


# ── Main comparison ─────────────────────────────────────────────────────────────
message   = sine(t, FM)
modulated = am_modulate(FC, message, t, mod_index=0.8)
received  = add_noise(modulated, snr_db=20)

rec_homo  = homodyne(received, t)
rec_het   = heterodyne(received, t)

# ── SNR sweep ───────────────────────────────────────────────────────────────────
snr_range = np.arange(5, 35, 2)
corr_homo, corr_het = [], []

for snr in snr_range:
    noisy = add_noise(modulated, snr_db=snr)
    corr_homo.append(pearsonr(message, homodyne(noisy, t))[0])
    corr_het.append( pearsonr(message, heterodyne(noisy, t))[0])

# ── Plot ────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 10))
fig.suptitle("Homodyne vs Heterodyne — Visual Comparison", fontsize=14, fontweight='bold')

gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.4)

# ── Row 0: original message ─────────────────────────────────────────────────────
ax_msg = fig.add_subplot(gs[0, :])
ax_msg.plot(t[SHOW]*1000, message[SHOW],   color='#1d9e75', lw=1.2, label='Original message (10 Hz)')
ax_msg.plot(t[SHOW]*1000, received[SHOW],  color='#aaaaaa', lw=0.6, alpha=0.6, label='Received (noisy AM)')
ax_msg.set_title("Input signals", fontsize=10)
ax_msg.set_xlabel("Time (ms)", fontsize=9)
ax_msg.set_ylabel("Amplitude", fontsize=9)
ax_msg.legend(fontsize=8)
ax_msg.grid(True, alpha=0.3)

# ── Row 1: time-domain recovery ─────────────────────────────────────────────────
ax_h = fig.add_subplot(gs[1, 0])
ax_h.plot(t[SHOW]*1000, message[SHOW],   color='#1d9e75', lw=1.2, ls='--', label='Original')
ax_h.plot(t[SHOW]*1000, rec_homo[SHOW],  color='#7f77dd', lw=1.0, label='Homodyne recovery')
ax_h.set_title("Homodyne — recovered signal", fontsize=10)
ax_h.set_xlabel("Time (ms)", fontsize=9)
ax_h.legend(fontsize=8)
ax_h.grid(True, alpha=0.3)

ax_he = fig.add_subplot(gs[1, 1])
ax_he.plot(t[SHOW]*1000, message[SHOW],  color='#1d9e75', lw=1.2, ls='--', label='Original')
ax_he.plot(t[SHOW]*1000, rec_het[SHOW],  color='#d85a30', lw=1.0, label='Heterodyne recovery')
ax_he.set_title("Heterodyne — recovered signal", fontsize=10)
ax_he.set_xlabel("Time (ms)", fontsize=9)
ax_he.legend(fontsize=8)
ax_he.grid(True, alpha=0.3)

# ── Overlay comparison ──────────────────────────────────────────────────────────
ax_ov = fig.add_subplot(gs[1, 2])
ax_ov.plot(t[SHOW]*1000, rec_homo[SHOW], color='#7f77dd', lw=1.0, label='Homodyne')
ax_ov.plot(t[SHOW]*1000, rec_het[SHOW],  color='#d85a30', lw=1.0, ls='--', label='Heterodyne')
ax_ov.set_title("Overlay comparison", fontsize=10)
ax_ov.set_xlabel("Time (ms)", fontsize=9)
ax_ov.legend(fontsize=8)
ax_ov.grid(True, alpha=0.3)

# ── Row 2: SNR sweep ─────────────────────────────────────────────────────────────
ax_snr = fig.add_subplot(gs[2, :])
ax_snr.plot(snr_range, corr_homo, 'o-', color='#7f77dd', lw=1.5, label='Homodyne')
ax_snr.plot(snr_range, corr_het,  's-', color='#d85a30', lw=1.5, label='Heterodyne')
ax_snr.axvline(20, color='gray', ls=':', lw=1, label='Demo SNR = 20 dB')
ax_snr.set_xlabel("SNR (dB)", fontsize=9)
ax_snr.set_ylabel("Pearson correlation with original", fontsize=9)
ax_snr.set_title("Recovery quality vs. channel noise — both techniques", fontsize=10)
ax_snr.set_ylim(0, 1.05)
ax_snr.legend(fontsize=9)
ax_snr.grid(True, alpha=0.3)

plt.savefig("outputs/03_comparison.png", dpi=150, bbox_inches='tight')
print("✓ Saved  outputs/03_comparison.png")
plt.show()
