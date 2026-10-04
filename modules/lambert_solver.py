import streamlit as st
from numpy import array, inner, clip, degrees, sin, cos, arccos, arcsin, sqrt, pi
from numpy.linalg import norm
import pandas as pd
from auxiliary.custom_visuals import divider, small_divider
from auxiliary.global_calculations import update_mu

def calc_lambert_short_way(input_data, way="short"):
    mu, r1x, r1y, r1z, r2x, r2y, r2z, dt = input_data
    
    r1_vec = array([r1x, r1y, r1z])
    r2_vec = array([r2x, r2y, r2z])
    
    r1 = norm(r1_vec)
    r2 = norm(r2_vec)
    
    cos_dtheta = clip(inner(r1_vec, r2_vec)/(r1*r2), -1.0, 1.0)
    dtheta_short = arccos(cos_dtheta)
    
    c_vec = r2_vec - r1_vec
    c = norm(c_vec)
    
    s = (r1 + r2 + c) / 2.0

    dtheta = dtheta_short if way == "short" else 2*pi - dtheta_short
    
    a_min = s / 2.0
    val = clip((s - c) / (2 * a_min), 0.0, 1.0)
    beta_min = 2 * arcsin(sqrt(val))
    t_min = sqrt(a_min**3 / mu) * (pi - (beta_min - sin(beta_min)))
    
    if way == "long":
            beta_min = -beta_min
            
    t_min = sqrt(a_min**3 / mu) * (pi - (beta_min - sin(beta_min)))
    
    t_diff = dt - t_min
    if abs(t_diff) < 1e-6:
        a = a_min
        alpha = pi
        beta = beta_min
    
    elif dt < t_min:
        def f(a_test):
            alf = 2 * arcsin(sqrt(clip(s / (2*a_test), 0.0, 1.0)))
            bet = 2 * arcsin(sqrt(clip((s - c) / (2*a_test), 0.0, 1.0)))
            if way == "long": bet = -bet
            return sqrt(a_test**3 / mu) * (alf - sin(alf) - (bet - sin(bet))) - dt
        
        low = a_min
        high = a_min * 1.5
        while f(high) > 0: high *= 2
            
        for _ in range(100):
            mid = (low + high) / 2
            if abs(f(mid)) < 1e-6: break
            if f(low) * f(mid) < 0: high = mid
            else: low = mid
        a = mid
        alpha = 2 * arcsin(sqrt(clip(s / (2*a), 0.0, 1.0)))
        beta = 2 * arcsin(sqrt(clip((s - c) / (2*a), 0.0, 1.0)))
        if way == "long": beta = -beta
    else:
        def f(a_test):
            alf = 2 * arcsin(sqrt(clip(s / (2*a_test), 0.0, 1.0)))
            bet = 2 * arcsin(sqrt(clip((s - c) / (2*a_test), 0.0, 1.0)))
            if way == "long": bet = -bet
            return sqrt(a_test**3 / mu) * ((2*pi - alf) + sin(alf) - (bet - sin(bet))) - dt
            
        low = a_min
        high = a_min * 1.5
        while f(high) < 0: high *= 2
            
        for _ in range(100):
            mid = (low + high) / 2
            if abs(f(mid)) < 1e-6: break
            if f(low) * f(mid) < 0: high = mid
            else: low = mid
        a = mid
        alpha = 2*pi - 2 * arcsin(sqrt(clip(s / (2*a), 0.0, 1.0)))
        beta = 2 * arcsin(sqrt(clip((s - c) / (2*a), 0.0, 1.0)))
        if way == "long": beta = -beta

    A = sqrt(mu / (4*a)) * (cos(alpha / 2) / sin(alpha / 2))
    B = sqrt(mu / (4*a)) * (cos(beta / 2) / sin(beta / 2))
    
    uc = c_vec / c
    rho_vec = r1_vec + r2_vec
    urho = rho_vec / norm(rho_vec)
    
    v1_vec = (B + A)*uc + (B - A)*urho
    v2_vec = (B + A)*uc - (B - A)*urho
    
    return {
        "r1": r1, "r2": r2, "dtheta": degrees(dtheta),
        "c_vec": c_vec, "c": c, "s": s,
        "a": a, "alpha": degrees(alpha), "beta": degrees(beta),
        "A": A, "B": B, "v1": v1_vec, "v2": v2_vec
    }


def main_lambert():
    if "lam_way" not in st.session_state:
        st.session_state.lam_way = "short"
    
    for param in ["r1x", "r1y", "r1z", "r2x", "r2y", "r2z", "dt"]:
        chave = f"lam_{param}"
        if chave not in st.session_state:
            st.session_state[chave] = None

    def set_way(w):
        st.session_state.lam_way = w

    col1, col2 = st.columns(2)
    with col1:
        st.title("AstroTools", anchor=False)
    with col2:
        titulo = "_Lambert (Short Way)_" if st.session_state.lam_way == "short" else "_Lambert (Long Way)_"
        st.title(titulo, anchor=False, text_alignment="right")
    divider()
    st.write("")

    col3, col4 = st.columns([3, 1], border=True)
    
    with col4:
        st.subheader("Import Data", help="Upload CSV: $x_1, y_1, z_1, x_2, y_2, z_2, \Delta t$", anchor=False, text_alignment="center")
        with st.container(horizontal_alignment="center"):
            uploaded_file = st.file_uploader("File Loader", label_visibility="collapsed", type=["csv"], key="uploader_lam", width=120)

    if uploaded_file is not None:
        if st.session_state.last_file != uploaded_file.name:
            df = pd.read_csv(uploaded_file, names=["r1x", "r1y", "r1z", "r2x", "r2y", "r2z", "dt"])
            
            st.session_state.lam_r1x = float(df["r1x"].iloc[0]) if not pd.isna(df["r1x"].iloc[0]) else None
            st.session_state.lam_r1y = float(df["r1y"].iloc[0]) if not pd.isna(df["r1y"].iloc[0]) else None
            st.session_state.lam_r1z = float(df["r1z"].iloc[0]) if not pd.isna(df["r1z"].iloc[0]) else None
            st.session_state.lam_r2x = float(df["r2x"].iloc[0]) if not pd.isna(df["r2x"].iloc[0]) else None
            st.session_state.lam_r2y = float(df["r2y"].iloc[0]) if not pd.isna(df["r2y"].iloc[0]) else None
            st.session_state.lam_r2z = float(df["r2z"].iloc[0]) if not pd.isna(df["r2z"].iloc[0]) else None
            st.session_state.lam_dt = float(df["dt"].iloc[0]) if not pd.isna(df["dt"].iloc[0]) else None
            
            st.session_state.last_file = uploaded_file.name
    else:
        st.session_state.last_file = None
    
    with col3:
        col5, col6 = st.columns(2, gap="large")
        with col5:
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$μ$**  $(km^3/s^2)$")
                mu_in = st.number_input("mu_lam", value=st.session_state.mu_val, label_visibility="collapsed", placeholder="Insert value")
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
            st.markdown("**Initial Position Vector ($\\vec{r}_1$)**")
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$x$**")
                r1x_in = st.number_input("r1x", value=st.session_state.lam_r1x, label_visibility="collapsed", placeholder="km", format="%.4f")
                st.session_state.lam_r1x = r1x_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$y$**")
                r1y_in = st.number_input("r1y", value=st.session_state.lam_r1y, label_visibility="collapsed", placeholder="km", format="%.4f")
                st.session_state.lam_r1y = r1y_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$z$**")
                r1z_in = st.number_input("r1z", value=st.session_state.lam_r1z, label_visibility="collapsed", placeholder="km", format="%.4f")
                st.session_state.lam_r1z = r1z_in

        with col8:
            st.markdown("**Final Position Vector ($\\vec{r}_2$)**")
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$x$**")
                r2x_in = st.number_input("r2x", value=st.session_state.lam_r2x, label_visibility="collapsed", placeholder="km", format="%.4f")
                st.session_state.lam_r2x = r2x_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$y$**")
                r2y_in = st.number_input("r2y", value=st.session_state.lam_r2y, label_visibility="collapsed", placeholder="km", format="%.4f")
                st.session_state.lam_r2y = r2y_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$z$**")
                r2z_in = st.number_input("r2z", value=st.session_state.lam_r2z, label_visibility="collapsed", placeholder="km", format="%.4f")
                st.session_state.lam_r2z = r2z_in

        small_divider()
        st.write("")

        col9, col10 = st.columns(2, gap="large")

        with col9:
            with st.container(vertical_alignment="center", horizontal=True):
                st.markdown("**$\Delta t$ ($s$)**")
                dt_in = st.number_input("dt_lam", value=st.session_state.lam_dt, label_visibility="collapsed", placeholder="Time of flight")
                st.session_state.lam_dt = dt_in

        with col10:
            with st.container(vertical_alignment="center", horizontal=True):
                st.button("**Short Way**", on_click=set_way, args=("short",),
                          type="primary" if st.session_state.lam_way == "short" else "secondary", use_container_width=True)
                st.button("**Long Way**", on_click=set_way, args=("long",), 
                          type="primary" if st.session_state.lam_way == "long" else "secondary", use_container_width=True)


        input_data = [
            st.session_state.mu_val, 
            st.session_state.lam_r1x, st.session_state.lam_r1y, st.session_state.lam_r1z,
            st.session_state.lam_r2x, st.session_state.lam_r2y, st.session_state.lam_r2z,
            st.session_state.lam_dt
        ]
        
    if None not in input_data:  
        divider()
        st.write("")
        with st.container():    
            output = calc_lambert_short_way(input_data, way=st.session_state.lam_way)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Initial Position ($r_1$)", f"{output['r1']:.2f} km", border=True)
            c2.metric("Final Position ($r_2$)", f"{output['r2']:.2f} km", border=True)
            c3.metric("Chord ($c$)", f"{output['c']:.2f} km", border=True)
            c4.metric("Semi-perimeter ($s$)", f"{output['s']:.2f} km", border=True)
            
            c5, c6, c7, c8 = st.columns(4)
            c5.metric("True Anomaly Delta ($\\Delta\\theta$)", f"{output['dtheta']:.2f}°", border=True)
            c6.metric("Angle $\\alpha$", f"{output['alpha']:.2f}°", border=True)
            c7.metric("Angle $\\beta$", f"{output['beta']:.2f}°", border=True)
            c8.metric("Semi-major Axis ($a$)", f"{output['a']:.2f} km", border=True)
            
            c9, c10, c11, c12 = st.columns(4)
            c9.metric("Factor $A$", f"{output['A']:.4f} km/s", border=True)
            c10.metric("Factor $B$", f"{output['B']:.4f} km/s", border=True)
            c11.metric("Initial Velocity ($v_1$)", f"{norm(output['v1']):.2f} km/s", border=True)
            c12.metric("Final Velocity ($v_2$)", f"{norm(output['v2']):.2f} km/s", border=True)
            
            small_divider()
            st.write(" ")
            
            def format_vec(vec, dec=2):
                x, y, z = vec
                return (f"${x:.{dec}f} \\hat{{\\imath}}$ ${y:+.{dec}f} \\hat{{\\jmath}}$ ${z:+.{dec}f} \\hat{{k}}$")

            st.metric("Chord Vector " + r"($\bm{\vec{c}}$)", format_vec(output['c_vec'], 2), border=True)
            st.metric("Initial Velocity Vector " + r"($\bm{\vec{v}_1}$)", format_vec(output['v1'], 4), border=True)
            st.metric("Final Velocity Vector " + r"($\bm{\vec{v}_2}$)", format_vec(output['v2'], 4), border=True)
            st.write("")

            with st.expander("Expand to copy data to clipboard", type="compact"):
                raw_data = (f"r1_mag = {output['r1']:.4f}\n"
                            f"r2_mag = {output['r2']:.4f}\n"
                            f"delta_theta = {output['dtheta']:.4f}\n"
                            f"c_mag = {output['c']:.4f}\n"
                            f"s = {output['s']:.4f}\n"
                            f"a = {output['a']:.4f}\n"
                            f"alpha = {output['alpha']:.4f}\n"
                            f"beta = {output['beta']:.4f}\n"
                            f"A = {output['A']:.6f}\n"
                            f"B = {output['B']:.6f}\n"
                            f"c_vec = [{output['c_vec'][0]:.4f}, {output['c_vec'][1]:.4f}, {output['c_vec'][2]:.4f}]\n"
                            f"v1_vec = [{output['v1'][0]:.6f}, {output['v1'][1]:.6f}, {output['v1'][2]:.6f}]\n"
                            f"v2_vec = [{output['v2'][0]:.6f}, {output['v2'][1]:.6f}, {output['v2'][2]:.6f}]")
                st.code(raw_data, language="python")