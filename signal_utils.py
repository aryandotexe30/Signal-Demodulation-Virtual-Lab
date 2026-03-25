"""
Shared signal generation and filter utilities
Used by all demodulation modules
"""

import numpy as np
from scipy.signal import butter, sosfiltfilt


# ── Time axis ──────────────────────────────────────────────────────────────────
def make_time(duration=1.0, fs=10000):
    """Return time array and sample-rate tuple."""
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    return t, fs


# ── Signal primitives ──────────────────────────────────────────────────────────
def sine(t, freq, amp=1.0, phase=0.0):
    return amp * np.sin(2 * np.pi * freq * t + phase)


def am_modulate(carrier_freq, message_signal, t, mod_index=0.8):
    """
    AM modulation:  s(t) = [1 + m*x(t)] * cos(2π fc t)
    Returns modulated signal.
    """
    carrier = np.cos(2 * np.pi * carrier_freq * t)
    return (1 + mod_index * message_signal) * carrier


def add_noise(signal, snr_db=20, rng=None):
    """Add AWGN at the specified SNR (dB)."""
    if rng is None:
        rng = np.random.default_rng(42)
    sig_power = np.mean(signal ** 2)
    noise_power = sig_power / (10 ** (snr_db / 10))
    noise = rng.normal(0, np.sqrt(noise_power), len(signal))
    return signal + noise


# ── Filters ────────────────────────────────────────────────────────────────────
def lowpass(signal, cutoff, fs, order=5):
    sos = butter(order, cutoff / (fs / 2), btype='low', output='sos')
    return sosfiltfilt(sos, signal)


def bandpass(signal, low, high, fs, order=4):
    sos = butter(order, [low / (fs / 2), high / (fs / 2)], btype='band', output='sos')
    return sosfiltfilt(sos, signal)


# ── Frequency axis helper ──────────────────────────────────────────────────────
def compute_spectrum(signal, fs):
    """Return positive-frequency axis and magnitude spectrum."""
    N = len(signal)
    freqs = np.fft.rfftfreq(N, d=1 / fs)
    mag = np.abs(np.fft.rfft(signal)) * 2 / N
    return freqs, mag
