import math
import numpy as np

def test_angles(V, I0, P0, Vsc, Isc, Psc):
    phi0 = math.acos(P0 / (math.sqrt(3) * V * I0))
    phisc = math.acos(Psc / (math.sqrt(3) * Vsc * Isc))
    return phi0, phisc

def build_circle(V_rated, I0, P0, Vsc, Isc, Psc):
    phi0, phisc = test_angles(V_rated, I0, P0, Vsc, Isc, Psc)
    Isc_rated = Isc * (V_rated / Vsc)
    # voltage reference along +y; currents lag to the right
    A = np.array([I0*math.sin(phi0),  I0*math.cos(phi0)])
    B = np.array([Isc_rated*math.sin(phisc), Isc_rated*math.cos(phisc)])
    ay = A[1]
    cx = (B[0]**2 + (ay - B[1])**2 - A[0]**2) / (2*(B[0] - A[0]))
    O = np.array([cx, ay]); R = abs(cx - A[0])
    return dict(A=A, B=B, O=O, R=R, phi0=phi0, phisc=phisc, Isc_rated=Isc_rated)

def dist_to_line(P, P1, P2):
    return abs(np.cross(P2-P1, P-P1) / np.linalg.norm(P2-P1))

def performance(P, V_rated, N_sync, circ):
    A, B = circ['A'], circ['B']
    I_P = np.linalg.norm(P)
    phi_P = math.atan2(P[0], P[1])          # angle from voltage (+y)
    pf = math.cos(phi_P)
    Pin = math.sqrt(3) * V_rated * I_P * pf
    d_out = dist_to_line(P, A, B)
    Pout = math.sqrt(3) * V_rated * d_out
    torque = Pout / (2*math.pi*N_sync/60)
    eff = (Pout / Pin * 100) if Pin > 0 else 0
    return dict(I=I_P, pf=pf, Pin=Pin, Pout=Pout, torque=torque, eff=eff)

def point_on_arc(t, circ):
    """t in [0,1] interpolates along the arc from A to B."""
    O, R, A, B = circ['O'], circ['R'], circ['A'], circ['B']
    aA = math.atan2(A[1]-O[1], A[0]-O[0])
    aB = math.atan2(B[1]-O[1], B[0]-O[0])
    # pick the shorter arc direction
    d = (aB - aA) % (2*math.pi)
    if d > math.pi: d -= 2*math.pi
    th = aA + t*d
    return O + R*np.array([math.cos(th), math.sin(th)])