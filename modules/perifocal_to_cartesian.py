import streamlit as st
from numpy import array, sin, cos, sqrt, pi, radians
from numpy.linalg import norm
import pandas as pd
from auxiliary.custom_visuals import divider, small_divider
from auxiliary.global_calculations import update_mu

def calc_perifocal_to_cartesian(input_data):
    mu, e, r_mag, theta_deg, Omega_deg, w_deg, i_deg = input_data
    
    theta = radians(theta_deg)
    Omega = radians(Omega_deg)
    w = radians(w_deg)
    inc = radians(i_deg)

    l = sqrt(r_mag * mu * (1 + e * cos(theta)))

    r_p = r_mag * cos(theta)
    r_q = r_mag * sin(theta)
    
    v_p = -(mu / l) * sin(theta)
    v_q = (mu / l) * (e + cos(theta))

    R11 = cos(Omega)*cos(w) - sin(Omega)*sin(w)*cos(inc)
    R12 = -cos(Omega)*sin(w) - sin(Omega)*cos(w)*cos(inc)
    
    R21 = sin(Omega)*cos(w) + cos(Omega)*sin(w)*cos(inc)
    R22 = -sin(Omega)*sin(w) + cos(Omega)*cos(w)*cos(inc)
    
    R31 = sin(w)*sin(inc)
    R32 = cos(w)*sin(inc)

    # 4. Vetores de Estado no Referencial Geocêntrico
    x = R11 * r_p + R12 * r_q
    y = R21 * r_p + R22 * r_q
    z = R31 * r_p + R32 * r_q

    vx = R11 * v_p + R12 * v_q
    vy = R21 * v_p + R22 * v_q
    vz = R31 * v_p + R32 * v_q

    # Grandezas Derivadas para Visualização
    if e < 1:
        a = (l**2 / mu) / (1 - e**2)
        rp = a * (1 - e)
        ra = a * (1 + e)
        T = 2 * pi * sqrt(abs(a)**3 / mu)
    else:
        a = float('inf')
        rp = (l**2 / mu) / (1 + e)
        ra = float('inf')
        T = float('inf')

    return {
        "r_eci": array([x, y, z]),
        "v_eci": array([vx, vy, vz]),
        "r_pq": array([r_p, r_q, 0]),
        "v_pq": array([v_p, v_q, 0]),
        "a": a, "rp": rp, "ra": ra, "T": T, "l": l
    }

def main_perifocal_to_cartesian():
    for param in ["e", "r", "theta", "Omega", "w", "i"]:
        chave = f"pc_{param}"
        if chave not in st.session_state:
            st.session_state[chave] = None

    col1, col2 = st.columns(2)
    with col1:
        st.title("AstroTools", anchor=False)
    with col2:
        st.title("_Perifocal → Cartesian_", anchor=False, text_alignment="right")
    divider()
    st.write("")

    col3, col4 = st.columns([3, 1], border=True)
    
    with col4:
        st.subheader("Import Data (optional)", help="Upload a .csv file in the format of $e, r, \theta, \Omega, \omega, i$", anchor=False, text_alignment="center")
        with st.container(horizontal_alignment="center"):
            uploaded_file = st.file_uploader("File Loader", label_visibility="collapsed", type=["csv"], width=120, key="uploader_pc")

    if uploaded_file is not None:
        if st.session_state.last_file != uploaded_file.name:
            df = pd.read_csv(uploaded_file, names=["e", "r", "theta", "Omega", "w", "i"])
            
            st.session_state.pc_e = float(df["e"].iloc[0]) if not pd.isna(df["e"].iloc[0]) else None
            st.session_state.pc_r = float(df["r"].iloc[0]) if not pd.isna(df["r"].iloc[0]) else None
            st.session_state.pc_theta = float(df["theta"].iloc[0]) if not pd.isna(df["theta"].iloc[0]) else None
            st.session_state.pc_Omega = float(df["Omega"].iloc[0]) if not pd.isna(df["Omega"].iloc[0]) else None
            st.session_state.pc_w = float(df["w"].iloc[0]) if not pd.isna(df["w"].iloc[0]) else None
            st.session_state.pc_i = float(df["i"].iloc[0]) if not pd.isna(df["i"].iloc[0]) else None
            
            st.session_state.last_file = uploaded_file.name
    else:
        st.session_state.last_file = None
    
    with col3:
        col5, col6 = st.columns(2, gap="large")
        with col5:
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$μ$**  $(km^3/s^2)$")
                mu_in = st.number_input("mu_pc", value=st.session_state.mu_val, label_visibility="collapsed", placeholder="Insert value")
                st.session_state.mu_val = mu_in

        with col6:
            with st.container(horizontal=True, vertical_alignment="center", horizontal_alignment="distribute"):
                st.button(label="$\mathbf{\mu}_{\mathrm{Earth}}$", type="secondary", width="stretch", on_click=update_mu, args=(398600.0,), key="pc_mu_e")
                st.button(label="$\mathbf{\mu}_{\mathrm{Sun}}$", type="secondary", width="stretch", on_click=update_mu, args=(132712440000.0,), key="pc_mu_s")
                st.button(label="$\mathbf{\mu}_{\mathrm{Moon}}$", type="secondary", width="stretch", on_click=update_mu, args=(4902.8,), key="pc_mu_m")
                st.button(label="$\mathbf{\mu}_{\mathrm{Mars}}$", type="secondary", width="stretch", on_click=update_mu, args=(42828.4,), key="pc_mu_ma")

        small_divider()
        st.write(" ")

        col7, col8 = st.columns(2, gap="large")
        with col7:
            st.markdown("**Orbital Size & Shape**")
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$e$**")
                e_in = st.number_input("e", value=st.session_state.pc_e, label_visibility="collapsed", placeholder="Eccentricity", format="%.6f")
                st.session_state.pc_e = e_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$r$**")
                r_in = st.number_input("r", value=st.session_state.pc_r, label_visibility="collapsed", placeholder="Radius (km)", format="%.4f")
                st.session_state.pc_r = r_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$\\theta$**")
                theta_in = st.number_input("theta", value=st.session_state.pc_theta, label_visibility="collapsed", placeholder="True Anomaly (°)", format="%.4f")
                st.session_state.pc_theta = theta_in
        with col8:
            st.markdown("**Euler Angles (°)**")
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$\Omega$**")
                Omega_in = st.number_input("Omega", value=st.session_state.pc_Omega, label_visibility="collapsed", placeholder="RAAN", format="%.4f")
                st.session_state.pc_Omega = Omega_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$\omega$**")
                w_in = st.number_input("w", value=st.session_state.pc_w, label_visibility="collapsed", placeholder="Arg. Periapsis", format="%.4f")
                st.session_state.pc_w = w_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$i$**")
                i_in = st.number_input("i", value=st.session_state.pc_i, label_visibility="collapsed", placeholder="Inclination", format="%.4f")
                st.session_state.pc_i = i_in

        input_data = [st.session_state.mu_val, st.session_state.pc_e, st.session_state.pc_r,
                      st.session_state.pc_theta, st.session_state.pc_Omega, st.session_state.pc_w, st.session_state.pc_i]
        
    if None not in input_data:  
        divider()
        st.write("")
        with st.container():    
            output = calc_perifocal_to_cartesian(input_data)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Semi-major Axis **($a$)**", f"{output['a']:.2f} km" if output['a'] != float('inf') else "∞", border=True)
            c2.metric("Periapsis Radius ($r_p$)", f"{output['rp']:.2f} km", border=True)
            c3.metric("Apoapsis Radius ($r_a$)", f"{output['ra']:.2f} km" if output['ra'] != float('inf') else "∞", border=True)
            c4.metric("Orbital Period ($T$)", f"{output['T']:.2f} s" if output['T'] != float('inf') else "∞", border=True)

            st.metric("Specific Angular Momentum ($l$)", f"{output['l']:.2f} km²/s", border=True)
            
            small_divider()
            st.write(" ")
            
            def format_vec(vec, dec=2):
                x, y, z = vec
                return (f"${x:.{dec}f} \\hat{{\\imath}}$ ${y:+.{dec}f} \\hat{{\\jmath}}$ ${z:+.{dec}f} \\hat{{k}}$")

            st.metric("Perifocal Position Vector " + r"($\mathbf{\vec{r}_{\mathrm{PQ}}}$)", format_vec(output['r_pq'], 2), border=True)
            st.metric("Perifocal Velocity Vector " + r"($\mathbf{\vec{v}_{\mathrm{PQ}}}$)", format_vec(output['v_pq'], 4), border=True)
            small_divider()
            st.write("")

            st.metric("Cartesian Position Vector " + r"($\mathbf{\vec{r}_{\mathrm{ECI}}}$)", format_vec(output['r_eci'], 2), border=True)
            st.metric("Cartesian Velocity Vector " + r"($\mathbf{\vec{v}_{\mathrm{ECI}}}$)", format_vec(output['v_eci'], 4), border=True)
            st.write("")

            with st.expander("Expand to copy data to clipboard", type="compact"):
                raw_data = (f"a = {output['a']:.4f}\n"
                            f"rp = {output['rp']:.4f}\n"
                            f"ra = {output['ra']:.4f}\n"
                            f"T = {output['T']:.4f}\n"
                            f"l = {output['l']:.4f}\n"
                            f"r_pq = [{output['r_pq'][0]:.4f}, {output['r_pq'][1]:.4f}, {output['r_pq'][2]:.4f}]\n"
                            f"v_pq = [{output['v_pq'][0]:.6f}, {output['v_pq'][1]:.6f}, {output['v_pq'][2]:.6f}]\n"
                            f"r_eci = [{output['r_eci'][0]:.4f}, {output['r_eci'][1]:.4f}, {output['r_eci'][2]:.4f}]\n"
                            f"v_eci = [{output['v_eci'][0]:.6f}, {output['v_eci'][1]:.6f}, {output['v_eci'][2]:.6f}]")
                st.code(raw_data, language="python")