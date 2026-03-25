"""
MODULE 4 — Biomedical Integration: ECG Signal Demodulation
===========================================================
Simulates an ECG-like signal (heart rate 60 bpm = 1 Hz)
modulated onto a carrier (as in some wireless body-area network
or capacitive coupling biosensor scenarios).

Also shows a pure ECG bandpass filtering pipeline identical
to the heterodyne concept: isolate the cardiac band from noise.

NOTE: wfdb (PhysioNet) download requires internet.
This module works fully OFFLINE using a synthetic ECG.
Uncomment the wfdb section at the bottom to use real data.

Run:  python 04_biomedical.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from utils.signal_utils import (
    make_time, am_modulate, add_noise,
    lowpass, bandpass, compute_spectrum
)

FS       = 5_000
DURATION = 2.0
FC       = 500      # carrier for wireless ECG scenario
HR_HZ    = 1.0      # 1 Hz = 60 bpm

t, fs = make_time(DURATION, FS)


# ── Synthetic ECG generator ─────────────────────────────────────────────────────
def synthetic_ecg(t, hr=1.0, noise_level=0.05):
    """
    Approximates a single-lead ECG using a sum of Gaussians
    representing P, QRS, and T waves at each heartbeat.
    """
    signal = np.zeros_like(t)
    dt     = 1.0 / hr           # seconds per beat
    n_beats = int(t[-1] / dt) + 2

    # Relative positions within one beat (0–1)
    beats_params = [
        # (offset, width, amplitude)  — P, Q, R, S, T
        (0.18, 0.03,  0.15),   # P wave
        (0.30, 0.01, -0.10),   # Q
        (0.33, 0.012, 1.00),   # R (dominant spike)
        (0.37, 0.01, -0.25),   # S
        (0.55, 0.05,  0.35),   # T wave
    ]
    for b in range(n_beats):
        t0 = b * dt
        for offset, width, amp in beats_params:
            center = t0 + offset * dt
            signal += amp * np.exp(-((t - center)**2) / (2 * width**2))

    rng = np.random.default_rng(7)
    signal += rng.normal(0, noise_level, len(t))
    return signal


# ── Signals ─────────────────────────────────────────────────────────────────────
ecg_clean  = synthetic_ecg(t, hr=HR_HZ, noise_level=0.02)

# Add EMG-like noise (muscle artefact at 50–150 Hz) + powerline (50 Hz)
rng        = np.random.default_rng(42)
emg_noise  = 0.3 * rng.normal(0, 1, len(t))
emg_noise  = bandpass(emg_noise, 50, 150, FS)
powerline  = 0.2 * np.sin(2 * np.pi * 50 * t)
ecg_noisy  = ecg_clean + emg_noise + powerline

# Cardiac bandpass (0.5–40 Hz) — equivalent to lock-in / heterodyne band selection
ecg_filtered = bandpass(ecg_noisy, 0.5, 40, FS)

# ── Wireless scenario: AM demodulation ─────────────────────────────────────────
# Imagine a capacitive ECG sensor that AM-modulates the signal onto 500 Hz
norm_ecg  = ecg_clean / np.max(np.abs(ecg_clean))    # normalise to ±1
modulated = am_modulate(FC, norm_ecg, t, mod_index=0.7)
received  = add_noise(modulated, snr_db=25)

# Homodyne demodulation
lo        = np.cos(2 * np.pi * FC * t)
recovered = lowpass(received * lo, 45, FS) * 2

# ── Spectra ─────────────────────────────────────────────────────────────────────
f_noisy, S_noisy   = compute_spectrum(ecg_noisy,    FS)
f_filt,  S_filt    = compute_spectrum(ecg_filtered, FS)
f_rcv,   S_rcv     = compute_spectrum(received,     FS)
f_rec,   S_rec     = compute_spectrum(recovered,    FS)

# ── Plot ────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 14))
fig.suptitle("Biomedical Integration — ECG Signal Processing & Wireless Demodulation",
             fontsize=13, fontweight='bold')

gs = gridspec.GridSpec(4, 2, figure=fig, hspace=0.6, wspace=0.35)

SHOW_ECG = slice(0, int(FS * 1.5))

# ── Row 0: clean vs noisy ECG ───────────────────────────────────────────────────
ax00 = fig.add_subplot(gs[0, :])
ax00.plot(t[SHOW_ECG], ecg_noisy[SHOW_ECG],  color='#aaaaaa', lw=0.7, alpha=0.8,
          label='Noisy ECG (+ EMG + powerline)')
ax00.plot(t[SHOW_ECG], ecg_clean[SHOW_ECG],  color='#d85a30', lw=1.2,
          label='Clean ECG (synthetic ground truth)')
ax00.set_title("① Raw ECG with artefacts — like a real bedside electrode", fontsize=10)
ax00.set_xlabel("Time (s)", fontsize=9)
ax00.set_ylabel("mV (normalised)", fontsize=9)
ax00.legend(fontsize=8)
ax00.grid(True, alpha=0.3)

# ── Row 1: filtering (heterodyne concept) ───────────────────────────────────────
ax10 = fig.add_subplot(gs[1, 0])
ax10.plot(t[SHOW_ECG], ecg_filtered[SHOW_ECG], color='#1d9e75', lw=1.2,
          label='After cardiac BPF (0.5–40 Hz)')
ax10.plot(t[SHOW_ECG], ecg_clean[SHOW_ECG],    color='#d85a30', lw=0.8, ls='--',
          label='Clean ECG')
ax10.set_title("② After bandpass filter — noise removed", fontsize=10)
ax10.set_xlabel("Time (s)", fontsize=9)
ax10.legend(fontsize=8)
ax10.grid(True, alpha=0.3)

ax11 = fig.add_subplot(gs[1, 1])
mask = f_noisy <= 200
ax11.plot(f_noisy[mask], S_noisy[mask], color='#aaaaaa', lw=0.9, label='Noisy')
ax11.plot(f_filt[mask],  S_filt[mask],  color='#1d9e75', lw=1.2, label='Filtered (0.5–40 Hz)')
ax11.axvspan(0, 40,  alpha=0.07, color='green', label='Cardiac band')
ax11.axvline(50, color='red', ls=':', lw=0.8, label='50 Hz powerline')
ax11.set_title("② Frequency spectrum — before & after", fontsize=10)
ax11.set_xlabel("Frequency (Hz)", fontsize=9)
ax11.legend(fontsize=7)
ax11.grid(True, alpha=0.3)

# ── Row 2: wireless AM scenario ─────────────────────────────────────────────────
ax20 = fig.add_subplot(gs[2, 0])
SHOW_RF = slice(0, int(FS * 0.02))
ax20.plot(t[SHOW_RF]*1000, received[SHOW_RF], color='#7f77dd', lw=0.8,
          label='Received wireless ECG (AM + noise)')
ax20.set_title(f"③ Wireless ECG — AM on {FC} Hz carrier", fontsize=10)
ax20.set_xlabel("Time (ms)", fontsize=9)
ax20.legend(fontsize=8)
ax20.grid(True, alpha=0.3)

ax21 = fig.add_subplot(gs[2, 1])
mask2 = f_rcv <= 700
ax21.plot(f_rcv[mask2], S_rcv[mask2], color='#7f77dd', lw=0.9)
ax21.axvline(FC, color='red', ls='--', lw=0.8, label=f'Carrier {FC} Hz')
ax21.set_title("③ AM spectrum — sidebands around carrier", fontsize=10)
ax21.set_xlabel("Frequency (Hz)", fontsize=9)
ax21.legend(fontsize=8)
ax21.grid(True, alpha=0.3)

# ── Row 3: recovered wireless ECG ───────────────────────────────────────────────
ax30 = fig.add_subplot(gs[3, 0])
ax30.plot(t[SHOW_ECG], norm_ecg[SHOW_ECG],  color='#d85a30', lw=1.0, ls='--',
          label='Original ECG')
ax30.plot(t[SHOW_ECG], recovered[SHOW_ECG], color='#185fa5', lw=1.2,
          label='Homodyne recovered')
ax30.set_title("④ Homodyne demodulation — ECG extracted from RF", fontsize=10)
ax30.set_xlabel("Time (s)", fontsize=9)
ax30.legend(fontsize=8)
ax30.grid(True, alpha=0.3)

ax31 = fig.add_subplot(gs[3, 1])
mask3 = f_rec <= 100
ax31.plot(f_rec[mask3], S_rec[mask3], color='#185fa5', lw=1.2)
ax31.axvline(HR_HZ, color='red', ls='--', lw=0.8, label=f'Heart rate ({HR_HZ} Hz = 60 bpm)')
ax31.set_title("④ Recovered spectrum — cardiac frequency visible", fontsize=10)
ax31.set_xlabel("Frequency (Hz)", fontsize=9)
ax31.legend(fontsize=8)
ax31.grid(True, alpha=0.3)

plt.savefig("outputs/04_biomedical.png", dpi=150, bbox_inches='tight')
print("✓ Saved  outputs/04_biomedical.png")
plt.show()


# ══════════════════════════════════════════════════════════════════════════════
# OPTIONAL — Uncomment below to load a REAL ECG from PhysioNet (needs internet)
# ══════════════════════════════════════════════════════════════════════════════
#
# import wfdb
# record = wfdb.rdrecord('mitdb/100', sampfrom=0, sampto=5000,
#                         pn_dir='mitdb')
# real_ecg = record.p_signal[:, 0]          # lead I
# real_fs   = record.fs                     # typically 360 Hz
# real_t    = np.arange(len(real_ecg)) / real_fs
# real_filt = bandpass(real_ecg, 0.5, 40, real_fs)
#
# plt.figure(figsize=(14, 4))
# plt.plot(real_t, real_ecg,  color='gray',    lw=0.7, label='Raw MIT-BIH ECG')
# plt.plot(real_t, real_filt, color='#1d9e75', lw=1.2, label='Filtered (0.5–40 Hz)')
# plt.xlabel("Time (s)"); plt.ylabel("mV"); plt.legend(); plt.grid(alpha=0.3)
# plt.title("Real ECG — MIT-BIH Arrhythmia Database Record 100")
# plt.tight_layout(); plt.show()
