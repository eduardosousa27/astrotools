import streamlit as st
from numpy import sin, cos, tan, arccos, arctan, arctan2, arctanh, sinh, cosh, tanh, sqrt, pi, radians, degrees, isnan, cbrt
from scipy.optimize import newton
import pandas as pd
from auxiliary.custom_visuals import divider, small_divider
from auxiliary.global_calculations import update_mu

def calc_theta_propagation(input_data):
    mu, e, l, theta0_deg, dt = input_data
    
    p = (l**2) / mu
    
    theta0_mod = theta0_deg % 360 if e < 1 else theta0_deg
    if e > 1:
        theta_inf = degrees(arccos(-1.0 / e))
        if abs(theta0_mod) >= theta_inf:
            return {"error": True, "msg": "Erro: A anomalia inicial excede o limite assintótico da órbita hiperbólica."}
            
    th0 = radians(theta0_mod)
    
    if e == 0:
        orbit_type = "Circular"
        a = p
        n = sqrt(mu / a**3)
        t0 = th0 / n
        period = 2*pi / n
    elif 0 < e < 1:
        orbit_type = "Elliptic"
        a = p / (1 - e**2)
        n = sqrt(mu / a**3)
        sin_E2 = sqrt(1 - e) * sin(th0/2)
        cos_E2 = sqrt(1 + e) * cos(th0/2)
        E0 = 2 * arctan2(sin_E2, cos_E2)
        t0 = (E0 - e * sin(E0)) / n
        period = 2*pi / n
    elif e == 1:
        orbit_type = "Parabolic"
        D0 = tan(th0/2)
        t0 = 0.5 * sqrt(p**3 / mu) * (D0 + (1.0/3.0) * D0**3)
        a = float('inf')
        period = float('inf')
    else:
        orbit_type = "Hyperbolic"
        a = p / (e**2 - 1)
        n = sqrt(mu / a**3)
        tanh_F2 = sqrt((e - 1)/(e + 1)) * tan(th0/2)
        F0 = 2 * arctanh(tanh_F2)
        t0 = (e * sinh(F0) - F0) / n
        period = float('inf')

    tf = t0 + dt
    revs = 0
    
    if e == 0:
        th_f = th0 + n * dt
        revs = int(th_f // (2*pi))
        th_f = th_f % (2*pi)
        
    elif 0 < e < 1:
        Mf = n * tf
        revs = int(Mf // (2*pi))
        M_mod = Mf % (2*pi)
        
        def kepler_eq(E): return E - e * sin(E) - M_mod
        def kepler_prime(E): return 1 - e * cos(E)
        Ef = newton(kepler_eq, x0=M_mod, fprime=kepler_prime)
        
        sin_th2 = sqrt(1 + e) * sin(Ef / 2)
        cos_th2 = sqrt(1 - e) * cos(Ef / 2)
        th_f = 2 * arctan2(sin_th2, cos_th2)
        if th_f < 0: th_f += 2*pi
        
    elif e == 1:
        np_parab = sqrt(mu / p**3)
        B = 3 * np_parab * tf
        A = cbrt(B + sqrt(B**2 + 1))
        Df = A - 1.0/A
        th_f = 2 * arctan(Df)
        
    else:
        Mh = n * tf
        def hyp_kepler(F): return e * sinh(F) - F - Mh
        def hyp_kepler_prime(F): return e * cosh(F) - 1
        
        import numpy as np
        F_guess = np.arcsinh(Mh / e)
        Ff = newton(hyp_kepler, x0=F_guess, fprime=hyp_kepler_prime)
        
        tanh_F2 = tanh(Ff / 2)
        tan_th2 = sqrt((e + 1) / (e - 1)) * tanh_F2
        th_f = 2 * arctan(tan_th2)

    return {
        "error": False, "orbit_type": orbit_type,
        "p": p, "a": a, "period": period,
        "t0": t0, "tf": tf, "dt": dt,
        "theta_f": degrees(th_f), "revs": revs
    }

def main_theta_propagation():
    for param in ["e", "l", "theta0", "dt"]:
        chave = f"prop_{param}"
        if chave not in st.session_state:
            st.session_state[chave] = None

    col1, col2 = st.columns(2)
    with col1:
        st.title("AstroTools", anchor=False)
    with col2:
        st.title("_Propagation (θ(t))_", anchor=False, text_alignment="right")
    divider()
    st.write("")

    col3, col4 = st.columns([3, 1], border=True)
    
    with col4:
        st.subheader("Import Data", help="Upload a .csv file in the format of $e, l, \\theta_i, \\Delta t$", anchor=False, text_alignment="center")
        with st.container(horizontal_alignment="center"):
            uploaded_file = st.file_uploader("File Loader", label_visibility="collapsed", type=["csv"], key="uploader_prop", width=120)

    if uploaded_file is not None:
        if st.session_state.last_file != uploaded_file.name:
            df = pd.read_csv(uploaded_file, names=["e", "l", "theta0", "dt"])
            
            st.session_state.prop_e = float(df["e"].iloc[0]) if not pd.isna(df["e"].iloc[0]) else None
            st.session_state.prop_l = float(df["l"].iloc[0]) if not pd.isna(df["l"].iloc[0]) else None
            st.session_state.prop_theta0 = float(df["theta0"].iloc[0]) if not pd.isna(df["theta0"].iloc[0]) else None
            st.session_state.prop_dt = float(df["dt"].iloc[0]) if not pd.isna(df["dt"].iloc[0]) else None
            
            st.session_state.last_file = uploaded_file.name
    else:
        st.session_state.last_file = None
    
    with col3:
        col5, col6 = st.columns(2, gap="large")
        with col5:
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$μ$**  $(km^3/s^2)$")
                mu_in = st.number_input("mu_prop", value=st.session_state.mu_val, label_visibility="collapsed", placeholder="Insert value")
                st.session_state.mu_val = mu_in

        with col6:
            with st.container(horizontal=True, vertical_alignment="center", horizontal_alignment="distribute"):
                st.button(label="$\mathbf{\mu}_{\mathrm{Earth}}$", type="primary" if st.session_state.mu_val == 398600.0 else "secondary",
                            width="stretch", on_click=update_mu, args=(398600.0,), key="lam_mu_e")
                st.button(label="$\mathbf{\mu}_{\mathrm{Sun}}$", type="primary" if st.session_state.mu_val == 132712440000.0 else "secondary",
                            width="stretch", on_click=update_mu, args=(132712440000.0,), key="lam_mu_s")
                st.button(label="$\mathbf{\mu}_{\mathrm{Moon}}$", type="primary" if st.session_state.mu_val == 4902.8 else "secondary",
                            width="stretch", on_click=update_mu, args=(4902.8,), key="lam_mu_m")
                st.button(label="$\mathbf{\mu}_{\mathrm{Mars}}$", type="primary" if st.session_state.mu_val == 42828.4 else "secondary",
                            width="stretch", on_click=update_mu, args=(42828.4,), key="lam_mu_ma")
        small_divider()
        st.write(" ")

        col7, col8 = st.columns(2, gap="large")
        with col7:
            st.markdown("**Orbit Shape**")
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$e$**")
                e_in = st.number_input("e", value=st.session_state.prop_e, label_visibility="collapsed", placeholder="Eccentricity", format="%.6f", min_value=0.0)
                st.session_state.prop_e = e_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$l$**")
                l_in = st.number_input("l", value=st.session_state.prop_l, label_visibility="collapsed", placeholder="Ang. Mom. (km²/s)", format="%.4f")
                st.session_state.prop_l = l_in
        with col8:
            st.markdown("**Initial State & Time**")
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$\\theta_i$**")
                th0_in = st.number_input("th0", value=st.session_state.prop_theta0, label_visibility="collapsed", placeholder="Initial True Anomaly (°)", format="%.4f")
                st.session_state.prop_theta0 = th0_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$\\Delta t$**")
                dt_in = st.number_input("dt_prop", value=st.session_state.prop_dt, label_visibility="collapsed", placeholder="Time elapsed (s)", format="%.2f")
                st.session_state.prop_dt = dt_in

        input_data = [
            st.session_state.mu_val, 
            st.session_state.prop_e, st.session_state.prop_l,
            st.session_state.prop_theta0, st.session_state.prop_dt
        ]
        
    if None not in input_data:  
        divider()
        st.write("")
        with st.container():    
            output = calc_theta_propagation(input_data)
            
            if output["error"]:
                st.error(output["msg"])
            else:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Orbital Regime", f"{output['orbit_type']}", border=True)
                c2.metric("Parameter ($p$)", f"{output['p']:.2f} km", border=True)
                c3.metric("Semi-major Axis ($a$)", f"{output['a']:.2f} km" if output['a'] != float('inf') else "∞", border=True)
                c4.metric("Orbital Period ($T$)", f"{output['period']:.2f} s" if output['period'] != float('inf') else "∞", border=True)
                
                c5, c6, c7, c8 = st.columns(4)
                c5.metric("$t_i$", f"{output['t0']:.2f} s", border=True)
                c6.metric("$t_f$", f"{output['tf']:.2f} s", border=True)
                c7.metric("$\\theta_f$", f"{output['theta_f']:.4f}°", border=True)
                c8.metric("Nº of Full Revolutions", f"{output['revs']}" if output['period'] != float('inf') else "N/A", border=True)
                
                small_divider()
                st.write(" ")
                
                with st.expander("Expand to copy data to clipboard", type="compact"):
                    raw_data = (f"orbit = '{output['orbit_type']}'\n"
                                f"p = {output['p']:.4f}\n"
                                f"a = {output['a']:.4f}\n"
                                f"period = {output['period']:.4f}\n"
                                f"t0 = {output['t0']:.6f}\n"
                                f"tf = {output['tf']:.6f}\n"
                                f"dt = {output['dt']:.6f}\n"
                                f"theta_f_deg = {output['theta_f']:.6f}\n"
                                f"completed_revolutions = {output['revs']}")
                    st.code(raw_data, language="python")