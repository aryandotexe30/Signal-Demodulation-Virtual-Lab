"""
MODULE 6 — Interactive Plotly Dashboard (Demo Showcase)
========================================================
Opens a browser with an interactive multi-panel dashboard.
Use this for your DEMO VIDEO — it looks professional and
lets you adjust parameters with sliders in real time.

Controls available:
  - SNR slider
  - LO frequency offset (shows demodulation degradation)
  - Carrier frequency selector

Run:  python 06_interactive_dashboard.py
Then open:  http://127.0.0.1:8050  in your browser
Press Ctrl+C to stop.

Requires: pip install dash
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.signal_utils import (
    make_time, sine, am_modulate, add_noise,
    lowpass, bandpass, compute_spectrum
)

# ── Constants ──────────────────────────────────────────────────────────────────
FS       = 10_000
DURATION = 0.5
FM       = 10

# ── Demodulators ───────────────────────────────────────────────────────────────
def demodulate_homo(received, t, fc, lo_offset=0):
    lo  = np.cos(2 * np.pi * (fc + lo_offset) * t)
    return lowpass(received * lo, 80, FS) * 2


def demodulate_het(received, t, fc, lo_offset=0):
    f_lo1   = fc + 150 + lo_offset
    f_if    = abs(fc - f_lo1)
    lo1     = np.cos(2 * np.pi * f_lo1 * t)
    stage1  = bandpass(received * lo1,
                       max(5, f_if - 30), f_if + 30, FS)
    lo2     = np.cos(2 * np.pi * f_if * t)
    return lowpass(stage1 * lo2, 30, FS) * 2


# ── Dash App ───────────────────────────────────────────────────────────────────
app = Dash(__name__)

app.layout = html.Div([

    html.H2("Signal Demodulation Visual Lab",
            style={'fontFamily': 'monospace', 'textAlign': 'center',
                   'marginBottom': '4px'}),
    html.P("Homodyne vs Heterodyne — Interactive Demo",
           style={'textAlign': 'center', 'color': '#888', 'marginTop': 0,
                  'fontFamily': 'monospace'}),

    html.Div([
        # Carrier frequency
        html.Div([
            html.Label("Carrier frequency (Hz)",
                       style={'fontFamily': 'monospace', 'fontSize': 13}),
            dcc.Slider(id='fc-slider', min=500, max=2000, step=100,
                       value=1000, marks={v: str(v) for v in range(500, 2001, 250)},
                       tooltip={"placement": "bottom"}),
        ], style={'marginBottom': 20}),

        # SNR
        html.Div([
            html.Label("Channel SNR (dB)",
                       style={'fontFamily': 'monospace', 'fontSize': 13}),
            dcc.Slider(id='snr-slider', min=0, max=40, step=2,
                       value=20, marks={v: str(v) for v in range(0, 41, 5)},
                       tooltip={"placement": "bottom"}),
        ], style={'marginBottom': 20}),

        # LO offset
        html.Div([
            html.Label("LO frequency offset (Hz) — 0 = perfect lock",
                       style={'fontFamily': 'monospace', 'fontSize': 13}),
            dcc.Slider(id='lo-slider', min=-50, max=50, step=2,
                       value=0, marks={v: str(v) for v in range(-50, 51, 10)},
                       tooltip={"placement": "bottom"}),
        ], style={'marginBottom': 20}),

    ], style={'maxWidth': 900, 'margin': '0 auto', 'padding': '0 30px'}),

    dcc.Graph(id='main-plot', style={'height': '780px'}),

    html.Div(id='quality-bar', style={
        'textAlign': 'center', 'fontFamily': 'monospace',
        'fontSize': 14, 'marginTop': 8, 'marginBottom': 20
    })

], style={'backgroundColor': '#0f1117', 'color': '#e0e0e0', 'minHeight': '100vh'})


@callback(
    Output('main-plot', 'figure'),
    Output('quality-bar', 'children'),
    Input('fc-slider', 'value'),
    Input('snr-slider', 'value'),
    Input('lo-slider', 'value'),
)
def update(fc, snr, lo_off):
    t, _  = make_time(DURATION, FS)
    SHOW  = slice(0, int(FS * 0.05))

    msg   = sine(t, FM)
    mod   = am_modulate(fc, msg, t, mod_index=0.8)
    rcv   = add_noise(mod, snr_db=snr)

    rec_h = demodulate_homo(rcv, t, fc, lo_off)
    rec_e = demodulate_het( rcv, t, fc, lo_off)

    f_mod, S_mod = compute_spectrum(mod, FS)
    f_rcv, S_rcv = compute_spectrum(rcv, FS)
    f_rh,  S_rh  = compute_spectrum(rec_h, FS)
    f_re,  S_re  = compute_spectrum(rec_e, FS)

    from scipy.stats import pearsonr
    q_h = pearsonr(msg, rec_h)[0]
    q_e = pearsonr(msg, rec_e)[0]

    colors = {
        'msg': '#1dc085', 'rcv': '#7f77dd',
        'hom': '#e07b3f', 'het': '#d4537e',
        'grid': '#2a2a3a', 'text': '#c0c0c0'
    }

    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=[
            f"Message signal ({FM} Hz)", f"AM spectrum — carrier at {fc} Hz",
            "Received signal (noisy)", "Received spectrum",
            "Homodyne vs Heterodyne recovery", "Recovery spectra (0–100 Hz)"
        ],
        vertical_spacing=0.12, horizontal_spacing=0.1
    )

    t_ms = t[SHOW] * 1000

    # Row 1
    fig.add_trace(go.Scatter(x=t_ms, y=msg[SHOW], line=dict(color=colors['msg'], width=1.5),
                             name='Message'), row=1, col=1)
    mask = f_mod <= fc + 200
    fig.add_trace(go.Scatter(x=f_mod[mask], y=S_mod[mask], line=dict(color=colors['msg'], width=1),
                             name='AM spectrum'), row=1, col=2)
    fig.add_vline(x=fc, line=dict(color='red', dash='dash', width=1), row=1, col=2)

    # Row 2
    fig.add_trace(go.Scatter(x=t_ms, y=rcv[SHOW], line=dict(color=colors['rcv'], width=0.8),
                             name=f'Received (SNR={snr} dB)'), row=2, col=1)
    mask2 = f_rcv <= fc + 200
    fig.add_trace(go.Scatter(x=f_rcv[mask2], y=S_rcv[mask2], line=dict(color=colors['rcv'], width=1),
                             name='Received spectrum'), row=2, col=2)

    # Row 3 — recovery
    fig.add_trace(go.Scatter(x=t_ms, y=msg[SHOW], line=dict(color='#555', width=1, dash='dot'),
                             name='Original'), row=3, col=1)
    fig.add_trace(go.Scatter(x=t_ms, y=rec_h[SHOW], line=dict(color=colors['hom'], width=1.5),
                             name=f'Homodyne (r={q_h:.3f})'), row=3, col=1)
    fig.add_trace(go.Scatter(x=t_ms, y=rec_e[SHOW], line=dict(color=colors['het'], width=1.5),
                             name=f'Heterodyne (r={q_e:.3f})'), row=3, col=1)

    mask3 = f_rh <= 100
    fig.add_trace(go.Scatter(x=f_rh[mask3], y=S_rh[mask3], line=dict(color=colors['hom'], width=1.5),
                             name='Homodyne spectrum'), row=3, col=2)
    fig.add_trace(go.Scatter(x=f_re[mask3], y=S_re[mask3], line=dict(color=colors['het'], width=1.5,
                             dash='dash'), name='Heterodyne spectrum'), row=3, col=2)
    fig.add_vline(x=FM, line=dict(color='green', dash='dash', width=1), row=3, col=2)

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#0f1117',
        plot_bgcolor='#0f1117',
        font=dict(family='monospace', color=colors['text'], size=11),
        legend=dict(bgcolor='rgba(0,0,0,0.3)', font=dict(size=10)),
        margin=dict(l=60, r=30, t=60, b=40),
    )
    fig.update_xaxes(gridcolor=colors['grid'], zerolinecolor=colors['grid'])
    fig.update_yaxes(gridcolor=colors['grid'], zerolinecolor=colors['grid'])

    quality_text = (
        f"Recovery quality  |  "
        f"Homodyne: r = {q_h:.4f}   |   "
        f"Heterodyne: r = {q_e:.4f}   |   "
        f"LO offset = {lo_off:+} Hz"
    )
    return fig, quality_text


if __name__ == '__main__':
    print("\n  ╔═══════════════════════════════════════════╗")
    print("  ║  Signal Demodulation Lab — Interactive   ║")
    print("  ║  Open:  http://127.0.0.1:8050            ║")
    print("  ╚═══════════════════════════════════════════╝\n")
    app.run(debug=False)
