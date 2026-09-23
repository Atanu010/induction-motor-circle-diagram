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
    "Operating position (0=no-load → 1=blocked rotor)",
    0.0,
    1.0,
    0.45,
    0.01
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
    fig, ax = plt.subplots(figsize=(7, 7))

    # ---------------------------------------------------------
    # 1. Draw current locus (circle)
    # ---------------------------------------------------------
    th = np.linspace(0, 2 * np.pi, 400)

    ax.plot(
        circ["O"][0] + circ["R"] * np.cos(th),
        circ["O"][1] + circ["R"] * np.sin(th),
        "b-",
        linewidth=2,
        label="Current locus (circle)"
    )

    # ---------------------------------------------------------
    # 2. Draw no-load point A
    # ---------------------------------------------------------
    ax.plot(
        circ["A"][0],
        circ["A"][1],
        "go",
        markersize=7,
        label="No-load I₀"
    )

    # ---------------------------------------------------------
    # 3. Draw blocked-rotor point B
    # ---------------------------------------------------------
    ax.plot(
        circ["B"][0],
        circ["B"][1],
        "ro",
        markersize=7,
        label="Blocked-rotor Iₛc"
    )

    # ---------------------------------------------------------
    # 4. Draw reference line AB
    # ---------------------------------------------------------
    A = circ["A"]
    B = circ["B"]

    ax.plot(
        [A[0], B[0]],
        [A[1], B[1]],
        "k--",
        linewidth=1.5,
        label="Reference line AB"
    )

    # ---------------------------------------------------------
    # 5. Draw operating point P
    # ---------------------------------------------------------
    ax.plot(
        P[0],
        P[1],
        "mo",
        markersize=8,
        label="Operating point P"
    )

   
    # ---------------------------------------------------------
    # 6. Projection of P onto AB
    # ---------------------------------------------------------
    AB = B - A
    AP = P - A

    denominator = np.dot(AB, AB)

    if denominator > 0:
        projection_factor = np.dot(AP, AB) / denominator
        Q = A + projection_factor * AB

        # Perpendicular construction from P to AB
        ax.plot(
            [P[0], Q[0]],
            [P[1], Q[1]],
            "k:",
            linewidth=1.5,
            label="Output-power construction"
        )

        # Projection point Q
        ax.plot(
            Q[0],
            Q[1],
            "ko",
            markersize=4
        )

    # ---------------------------------------------------------
    # 7. Circle centre
    # ---------------------------------------------------------
    ax.plot(
        circ["O"][0],
        circ["O"][1],
        "kx",
        markersize=9,
        markeredgewidth=2,
        label="Center O"
    )

    # ---------------------------------------------------------
    # 8. Labels
    # ---------------------------------------------------------
   ax.annotate(
    "A — No-load",
    xy=A,
    xytext=(10, 12),
    textcoords="offset points"
)

    ax.annotate(
        "B — Blocked rotor",
        xy=B,
        xytext=(8, 8),
        textcoords="offset points"
    )

    ax.annotate(
        "P — Operating point",
        xy=P,
        xytext=(8, 8),
        textcoords="offset points"
    )

   ax.annotate(
    "O — Centre",
    xy=circ["O"],
    xytext=(10, -20),
    textcoords="offset points"
)

    # ---------------------------------------------------------
    # 9. Formatting
    # ---------------------------------------------------------
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.35)

    ax.set_xlabel("Active current component (A)")
    ax.set_ylabel("Reactive current component (A)")

    ax.set_title(
        f"Induction Motor Circle Diagram | "
        f"Ns = {N_sync:.1f} rpm"
    )

    ax.legend(
    fontsize=8,
    loc="lower right"
)

    st.pyplot(fig)

with c2:
    st.subheader("Performance @ Operating Point")

    st.metric(
        "Stator current",
        f"{perf['I']:.2f} A"
    )

    st.metric(
        "Power factor",
        f"{perf['pf']:.3f}"
    )

    st.metric(
        "Input power",
        f"{perf['Pin']:.1f} W"
    )

    st.metric(
        "Output power",
        f"{perf['Pout']:.1f} W"
    )

    st.metric(
        "Operating position",
        f"{load_factor:.2f}"
    )

    st.metric(
        "Rotor speed",
        f"{perf['speed']:.1f} rpm"
    )

    st.metric(
        "Torque",
        f"{perf['torque']:.2f} N·m"
    )

    st.metric(
        "Efficiency",
        f"{perf['eff']:.1f} %"
    )
