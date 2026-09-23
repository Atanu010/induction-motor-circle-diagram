import streamlit as st
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from circle_diagram import build_circle, performance, point_on_arc

st.set_page_config(page_title="Circle Diagram — Induction Motor", layout="wide")
st.title("⚡ 3-Phase Induction Motor — Circle Diagram Analyzer")

st.sidebar.header("Test Data (per phase / line values)")
V  = st.sidebar.number_input("Rated voltage V (line, V)", 440.0)
I0 = st.sidebar.number_input("No-load current I0 (A)", 6.0)
P0 = st.sidebar.number_input("No-load power P0 (W)", 300.0)
Vsc = st.sidebar.number_input("Blocked-rotor voltage Vsc (V)", 100.0)
Isc = st.sidebar.number_input("Blocked-rotor current Isc (A)", 40.0)
Psc = st.sidebar.number_input("Blocked-rotor power Psc (W)", 1200.0)
f   = st.sidebar.number_input("Frequency (Hz)", 50.0)
poles = st.sidebar.number_input("Poles", 4)
N_sync = 120*f/poles

circ = build_circle(V, I0, P0, Vsc, Isc, Psc)
load_factor = st.sidebar.slider(
    "Operating point",
    min_value=0.0,
    max_value=1.0,
    value=0.45,
    step=0.01,
    help="0 = no-load end of the circle, 1 = blocked-rotor end."
)

P = point_on_arc(load_factor, circ)

# Approximate operating slip used only for the
# performance display. This keeps the current
# circle-diagram model internally consistent.
slip = load_factor

perf = performance(
    P,
    V,
    N_sync,
    circ,
    slip
)

c1, c2 = st.columns([2, 1])
with c1:
    fig, ax = plt.subplots(figsize=(7,7))
    th = np.linspace(0, 2*np.pi, 400)
    ax.plot(circ['O'][0]+circ['R']*np.cos(th), circ['O'][1]+circ['R']*np.sin(th), 'b-', label='Current locus (circle)')
    ax.plot([0, circ['A'][0]], [0, circ['A'][1]], 'go-', label='No-load I0')
    ax.plot([0, circ['B'][0]], [0, circ['B'][1]], 'ro-', label='Blocked-rotor Isc')
    ax.plot([circ['A'][0], circ['B'][0]], [circ['A'][1], circ['B'][1]], 'k--', label='Output line AB')
    ax.plot([0, P[0]], [0, P[1]], 'm-o', label='Operating point')
    ax.plot(circ['O'][0], circ['O'][1], 'kx', ms=9, label='Center')
    ax.set_aspect('equal'); ax.grid(True); ax.legend(fontsize=8)
    ax.set_title(f"Circle Diagram  |  Ns = {N_sync:.0f} rpm")
    st.pyplot(fig)

with c2:
    st.subheader("Performance @ operating point")
    st.metric("Stator current", f"{perf['I']:.2f} A")
    st.metric("Power factor", f"{perf['pf']:.3f}")
    st.metric("Input power", f"{perf['Pin']:.1f} W")
    st.metric("Output power (gross)", f"{perf['Pout']:.1f} W")
    st.metric("Torque", f"{perf['torque']:.2f} N·m")
    st.metric("Efficiency", f"{perf['eff']:.1f} %")
