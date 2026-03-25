"""
MODULE 5 — Mechanical Integration: Lock-in Amplifier / Vibration Sensing
=========================================================================
Models a rotating machine bearing with a developing fault.

The scenario:
  - Motor running at 200 Hz (12,000 RPM)
  - A bearing fault introduces an amplitude-modulated sideband
  - The fault grows from zero to a detectable level over 2 seconds
  - Lock-in (homodyne) demodulation extracts the fault envelope
    even when it is buried in 0 dB noise (SNR = 0!)

This is identical in math to homodyne demodulation:
  Reference = 200 Hz (from a tachometer or shaft encoder)
  Sensor output = vibration signal
  × Reference → Low-pass filter → fault envelope

Also shows:
  - Frequency response (waterfall) of a sweep
  - Phase detection (the imaginary component after LO multiply)

Run:  python 05_mechanical.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from utils.signal_utils import (
    make_time, add_noise, lowpass, bandpass, compute_spectrum
)

FS          = 20_000
DURATION    = 2.0
F_MOTOR     = 200      # fundamental vibration (Hz)
F_FAULT     = 4        # fault modulation frequency (Hz)
SNR_DB      = 0        # 0 dB SNR — extremely noisy!
LPF_CUTOFF  = 20

t, fs = make_time(DURATION, FS)


# ── Synthetic vibration signal ──────────────────────────────────────────────────
def bearing_signal(t, f_motor=F_MOTOR, f_fault=F_FAULT):
    """
    Healthy motor: carrier at f_motor + harmonics
    Faulty bearing: amplitude modulation by slowly growing fault envelope
    """
    # Fault grows linearly from 0 to full amplitude
    fault_growth  = np.linspace(0, 1, len(t))
    fault_env     = fault_growth * np.sin(2 * np.pi * F_FAULT * t)

    # Healthy vibration (motor + harmonics)
    healthy       = (1.0  * np.cos(2 * np.pi * F_MOTOR     * t) +
                     0.3  * np.cos(2 * np.pi * F_MOTOR * 2 * t) +
                     0.15 * np.cos(2 * np.pi * F_MOTOR * 3 * t))

    # Faulty component: AM-modulated by fault envelope
    faulty_comp   = (1 + 0.6 * fault_env) * np.cos(2 * np.pi * F_MOTOR * t)

    return faulty_comp + 0.3 * np.cos(2 * np.pi * F_MOTOR * 2 * t), fault_env


vib_signal, true_fault_env = bearing_signal(t)
vib_noisy   = add_noise(vib_signal, snr_db=SNR_DB)

# ── Lock-in demodulation (homodyne) ─────────────────────────────────────────────
ref_cos  = np.cos(2 * np.pi * F_MOTOR * t)   # in-phase
ref_sin  = np.sin(2 * np.pi * F_MOTOR * t)   # quadrature

I_raw    = vib_noisy * ref_cos
Q_raw    = vib_noisy * ref_sin

I_filt   = lowpass(I_raw, LPF_CUTOFF, FS)    # in-phase component
Q_filt   = lowpass(Q_raw, LPF_CUTOFF, FS)    # quadrature component

amplitude = 2 * np.sqrt(I_filt**2 + Q_filt**2)   # magnitude
phase_deg = np.degrees(np.arctan2(Q_filt, I_filt))  # phase angle

# ── Spectra ─────────────────────────────────────────────────────────────────────
f_raw, S_raw = compute_spectrum(vib_noisy,   FS)
f_clean, S_c = compute_spectrum(vib_signal,  FS)
f_amp, S_amp = compute_spectrum(amplitude,   FS)

# ── Plot ────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 14))
fig.suptitle("Mechanical Integration — Lock-in Amplifier / Bearing Fault Detection",
             fontsize=13, fontweight='bold')

gs = gridspec.GridSpec(4, 2, figure=fig, hspace=0.58, wspace=0.38)

SHOW_T  = slice(0, int(FS * 0.05))      # first 50 ms (time zoom)
SHOW_T2 = slice(0, len(t))              # full 2 s (envelope)

# ── Row 0: raw vibration signal ─────────────────────────────────────────────────
ax00 = fig.add_subplot(gs[0, 0])
ax00.plot(t[SHOW_T]*1000, vib_noisy[SHOW_T], color='#aaaaaa', lw=0.6, label='Noisy vibration (SNR = 0 dB)')
ax00.plot(t[SHOW_T]*1000, vib_signal[SHOW_T],color='#d85a30', lw=1.0, label='Clean signal')
ax00.set_title("① Raw accelerometer signal — motor at 200 Hz", fontsize=10)
ax00.set_xlabel("Time (ms)", fontsize=9)
ax00.set_ylabel("Acceleration", fontsize=9)
ax00.legend(fontsize=8)
ax00.grid(True, alpha=0.3)

ax01 = fig.add_subplot(gs[0, 1])
mask = f_raw <= 1000
ax01.plot(f_raw[mask],   S_raw[mask],  color='#aaaaaa', lw=0.8, label='Noisy')
ax01.plot(f_clean[mask], S_c[mask],    color='#d85a30', lw=1.2, label='Clean')
ax01.axvline(F_MOTOR,   color='green', ls='--', lw=0.9, label=f'Motor {F_MOTOR} Hz')
ax01.axvline(F_MOTOR*2, color='green', ls=':',  lw=0.7)
ax01.set_title("① Spectrum — motor harmonics", fontsize=10)
ax01.set_xlabel("Frequency (Hz)", fontsize=9)
ax01.legend(fontsize=8)
ax01.grid(True, alpha=0.3)

# ── Row 1: I and Q channels ─────────────────────────────────────────────────────
ax10 = fig.add_subplot(gs[1, 0])
ax10.plot(t[SHOW_T]*1000, I_filt[SHOW_T], color='#185fa5', lw=1.0, label='I (in-phase)')
ax10.plot(t[SHOW_T]*1000, Q_filt[SHOW_T], color='#d4537e', lw=1.0, label='Q (quadrature)')
ax10.set_title("② Lock-in I/Q channels after LPF", fontsize=10)
ax10.set_xlabel("Time (ms)", fontsize=9)
ax10.legend(fontsize=8)
ax10.grid(True, alpha=0.3)

ax11 = fig.add_subplot(gs[1, 1])
IQ_show = slice(0, int(FS * 0.5))
ax11.scatter(I_filt[IQ_show], Q_filt[IQ_show],
             c=t[IQ_show], cmap='plasma', s=1.5, alpha=0.6)
ax11.set_title("② I/Q constellation — rotating phase = fault onset", fontsize=10)
ax11.set_xlabel("I component", fontsize=9)
ax11.set_ylabel("Q component", fontsize=9)
ax11.grid(True, alpha=0.3)
ax11.set_aspect('equal')

# ── Row 2: extracted fault envelope ────────────────────────────────────────────
ax20 = fig.add_subplot(gs[2, :])
ax20.plot(t, vib_noisy * 0.05, color='#cccccc', lw=0.4, alpha=0.5, label='Noisy signal (scaled ×0.05)')
ax20.plot(t, amplitude,         color='#1d9e75', lw=1.5, label='Lock-in amplitude (fault envelope)')
ax20.plot(t, true_fault_env,    color='#d85a30', lw=1.2, ls='--', label='True fault envelope (ground truth)')
ax20.set_title("③ Fault envelope — extracted by lock-in at SNR = 0 dB", fontsize=10)
ax20.set_xlabel("Time (s)", fontsize=9)
ax20.set_ylabel("Amplitude", fontsize=9)
ax20.legend(fontsize=9)
ax20.grid(True, alpha=0.3)
ax20.text(0.5, 0.85, "← Healthy bearing | Fault growing →",
          transform=ax20.transAxes, ha='center', fontsize=9, color='gray')

# ── Row 3: phase and spectrum of envelope ───────────────────────────────────────
ax30 = fig.add_subplot(gs[3, 0])
ax30.plot(t, phase_deg, color='#7f77dd', lw=0.8)
ax30.set_title("④ Instantaneous phase — detects fault orientation change", fontsize=10)
ax30.set_xlabel("Time (s)", fontsize=9)
ax30.set_ylabel("Phase (°)", fontsize=9)
ax30.grid(True, alpha=0.3)

ax31 = fig.add_subplot(gs[3, 1])
mask2 = f_amp <= 50
ax31.plot(f_amp[mask2], S_amp[mask2], color='#1d9e75', lw=1.2)
ax31.axvline(F_FAULT, color='red', ls='--', lw=0.9, label=f'Fault freq {F_FAULT} Hz')
ax31.set_title("④ Envelope spectrum — fault frequency identified", fontsize=10)
ax31.set_xlabel("Frequency (Hz)", fontsize=9)
ax31.legend(fontsize=8)
ax31.grid(True, alpha=0.3)

plt.savefig("outputs/05_mechanical.png", dpi=150, bbox_inches='tight')
print("✓ Saved  outputs/05_mechanical.png")
plt.show()
