import streamlit as st
from numpy import sin, cos, tan, arccos, arctan2, arctanh, sinh, sqrt, pi, radians, degrees, isnan
import pandas as pd
from auxiliary.custom_visuals import divider, small_divider
from auxiliary.global_calculations import update_mu

def calc_time_of_flight(input_data):
    mu, e, l, theta0_deg, thetaf_deg = input_data
    
    p = (l**2) / mu
    
    def get_time(theta_deg):
        revs = int(theta_deg // 360) if e < 1 else 0
        theta_mod = theta_deg % 360 if e < 1 else theta_deg
        
        if e > 1:
            theta_inf = degrees(arccos(-1.0 / e))
            if abs(theta_mod) >= theta_inf:
                return float('nan'), "Hiperbólica (Invalida)", float('inf'), float('inf')
                
        theta = radians(theta_mod)
        
        if e == 0:
            a = p
            n = sqrt(mu / a**3)
            t_mod = theta / n
            period = 2*pi / n
            return t_mod + revs * period, "Circular", a, period
            
        elif 0 < e < 1:
            a = p / (1 - e**2)
            n = sqrt(mu / a**3)
            
            sin_E2 = sqrt(1 - e) * sin(theta/2)
            cos_E2 = sqrt(1 + e) * cos(theta/2)
            E = 2 * arctan2(sin_E2, cos_E2)
            if E < 0: E += 2*pi
            
            M = E - e * sin(E)
            t_mod = M / n
            period = 2*pi / n
            return t_mod + revs * period, "Elliptic", a, period
            
        elif e == 1:
            D = tan(theta/2)
            t = 0.5 * sqrt(p**3 / mu) * (D + (1.0/3.0) * D**3)
            return t, "Parabolic", float('inf'), float('inf')
            
        else:
            a = p / (e**2 - 1)
            n = sqrt(mu / a**3)
            
            tanh_F2 = sqrt((e - 1)/(e + 1)) * tan(theta/2)
            F = 2 * arctanh(tanh_F2)
            
            M_h = e * sinh(F) - F
            t = M_h / n
            return t, "Hyperbolic", a, float('inf')

    t0, orbit_type0, a, period = get_time(theta0_deg)
    tf, orbit_typef, _, _ = get_time(thetaf_deg)
    
    dt = tf - t0
    
    return {
        "orbit_type": orbit_type0 if not isnan(t0) else orbit_typef,
        "p": p, "a": a, "period": period,
        "t0": t0, "tf": tf, "dt": dt
    }


def main_time_of_flight():
    for param in ["e", "l", "theta0", "thetaf"]:
        chave = f"tof_{param}"
        if chave not in st.session_state:
            st.session_state[chave] = None

    col1, col2 = st.columns(2)
    with col1:
        st.title("AstroTools", anchor=False)
    with col2:
        st.title("_Time of Flight_", anchor=False, text_alignment="right")
    divider()
    st.write("")

    col3, col4 = st.columns([3, 1], border=True)
    
    with col4:
        st.subheader("Import Data", help="Upload a .csv file in the format of $e, l, \\theta_i, \\theta_f$", anchor=False, text_alignment="center")
        with st.container(horizontal_alignment="center"):
            uploaded_file = st.file_uploader("File Loader", label_visibility="collapsed", type=["csv"], key="uploader_tof", width=120)

    if uploaded_file is not None:
        if st.session_state.last_file != uploaded_file.name:
            df = pd.read_csv(uploaded_file, names=["e", "l", "theta0", "thetaf"])
            
            st.session_state.tof_e = float(df["e"].iloc[0]) if not pd.isna(df["e"].iloc[0]) else None
            st.session_state.tof_l = float(df["l"].iloc[0]) if not pd.isna(df["l"].iloc[0]) else None
            st.session_state.tof_theta0 = float(df["theta0"].iloc[0]) if not pd.isna(df["theta0"].iloc[0]) else None
            st.session_state.tof_thetaf = float(df["thetaf"].iloc[0]) if not pd.isna(df["thetaf"].iloc[0]) else None
            
            st.session_state.last_file = uploaded_file.name
    else:
        st.session_state.last_file = None
    
    with col3:
        col5, col6 = st.columns(2, gap="large")
        with col5:
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$μ$**  $(km^3/s^2)$")
                mu_in = st.number_input("mu_tof", value=st.session_state.mu_val, label_visibility="collapsed", placeholder="Insert value")
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
                e_in = st.number_input("e", value=st.session_state.tof_e, label_visibility="collapsed", placeholder="Eccentricity", format="%.6f", min_value=0.0)
                st.session_state.tof_e = e_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$l$**")
                l_in = st.number_input("l", value=st.session_state.tof_l, label_visibility="collapsed", placeholder="Ang. Mom. (km²/s)", format="%.4f")
                st.session_state.tof_l = l_in
        with col8:
            st.markdown("**True Anomalies (°)**")
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$\\theta_i$**")
                th0_in = st.number_input("th0", value=st.session_state.tof_theta0, label_visibility="collapsed", placeholder="Initial Angle", format="%.4f")
                st.session_state.tof_theta0 = th0_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$\\theta_f$**")
                thf_in = st.number_input("thf", value=st.session_state.tof_thetaf, label_visibility="collapsed", placeholder="Final Angle", format="%.4f")
                st.session_state.tof_thetaf = thf_in

        input_data = [
            st.session_state.mu_val, 
            st.session_state.tof_e, st.session_state.tof_l,
            st.session_state.tof_theta0, st.session_state.tof_thetaf
        ]
        
    if None not in input_data:  
        divider()
        st.write("")
        with st.container():    
            output = calc_time_of_flight(input_data)
            
            if isnan(output['dt']):
                st.error("Geometric Error. The true anomalies exceed the asymptotic limit. The satellite is at infinity.")
            else:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Orbital Regime", f"{output['orbit_type']}", border=True)
                c2.metric("Parameter ($p$)", f"{output['p']:.2f} km", border=True)
                c3.metric("Semi-major Axis ($a$)", f"{output['a']:.2f} km" if output['a'] != float('inf') else "∞", border=True)
                c4.metric("Orbital Period ($T$)", f"{output['period']:.2f} s" if output['period'] != float('inf') else "∞", border=True)
                
                c5, c6, c7, c8 = st.columns(4)
                c5.metric("$t_i$", f"{output['t0']:.2f} s", border=True)
                c6.metric("$t_f$", f"{output['tf']:.2f} s", border=True)
                c7.metric("Time of Flight ($\\Delta t$)", f"{output['dt']:.2f} s", border=True)
                c8.metric("Time of Flight (Hours)", f"{abs(output['dt']) / 3600:.2f} h", border=True)
                
                st.write(" ")
                
                with st.expander("Expand to copy data to clipboard", type="compact"):
                    raw_data = (f"orbit = '{output['orbit_type']}'\n"
                                f"p = {output['p']:.4f}\n"
                                f"a = {output['a']:.4f}\n"
                                f"period = {output['period']:.4f}\n"
                                f"ti = {output['t0']:.6f}\n"
                                f"tf = {output['tf']:.6f}\n"
                                f"dt_seconds = {output['dt']:.6f}\n"
                                f"dt_hours = {abs(output['dt']) / 3600:.6f}\n"
                                f"dt_days = {abs(output['dt']) / 86400:.6f}")
                    st.code(raw_data, language="python")