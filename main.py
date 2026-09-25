import streamlit as st
import plotly.graph_objects as go
from numpy import array, inner, cross, clip, degrees, sin, cos, arcsin, arccos, arctan2, sqrt, pi, linspace, radians
from numpy.linalg import norm
import pandas as pd

if "option" not in st.session_state:
    st.session_state.option = "homepage"
if "mu_val" not in st.session_state:
    st.session_state.mu_val = 398600.0
if "last_file" not in st.session_state:
    st.session_state.last_file = None

st.set_page_config(page_title="AstroTools", page_icon="assets/astro_tools_logo.png", layout="wide", initial_sidebar_state="expanded")

for eixo in ["x", "y", "z", "vx", "vy", "vz"]:
    chave = f"cp_{eixo}"
    if chave not in st.session_state:
        st.session_state[chave] = None

def set_option_homepage():
    st.session_state.option = "homepage"

def set_option_cartesian_to_perifocal():
    st.session_state.option = "cartesian_to_perifocal"

def update_mu(val):
    st.session_state.mu_val = val

def divider():
    st.markdown("""<div style="height: 1px;
                background-color: #21c647;
                border-radius: 999px;
                margin: 1rem 0; "></div>""",
                unsafe_allow_html=True)

def small_divider():
    st.markdown("""<div style="height: 0.5px;
                background-color: #696969;
                border-radius: 999px;
                margin: 0rem 0; "></div>""",
                unsafe_allow_html=True)

def calc_cartesian_to_perifocal(input):
    r = array([input[0],
               input[1],
               input[2]])
    r_val = norm(r)

    v = array([input[3],
               input[4],
               input[5]])
    v_val = norm(v)

    k = array([0,
               0,
               1])

    l = cross(r, v)
    l_val = norm(l)

    i = degrees(arccos(clip(l[2]/l_val, -1.0, 1.0)))

    n = cross(k, l)
    n_val = norm(n)

    if n_val != 0:
        if n[1] >= 0: omega = degrees(arccos(clip(n[0]/n_val, -1.0, 1.0)))
        else: omega = 360 - degrees(arccos(clip(n[0]/n_val, -1.0, 1.0)))
    else: omega = 0.0

    mu = input[6]
    vr = inner((r/(r_val)), v)
    e = (1/mu) * ((v_val**2 - (mu/(r_val))) * r - r_val * vr * v)
    e_val = norm(e)

    if n_val != 0 and e_val != 0:
        if e[2] >= 0: w = degrees(arccos(clip(inner(n, e)/(n_val*e_val), -1.0, 1.0)))
        else: w = 360 - degrees(arccos(clip(inner(n, e)/(n_val*e_val), -1.0, 1.0)))
    else:
        w = 0.0

    if e_val != 0:
        if inner(r, v) >= 0: theta = degrees(arccos(clip(inner(e, r)/(e_val*r_val), -1.0, 1.0)))
        else: theta = 360 - degrees(arccos(clip(inner(e, r)/(e_val*r_val), -1.0, 1.0)))
    else:
        theta = 0.0

    rp = (l_val)**2 / (mu * (1 + e_val))
    if e_val < 1:
        ra = (l_val)**2 / (mu * (1 - e_val))
        a = 0.5 * (rp + ra)
        t = 2 * pi * a**1.5 / sqrt(mu)
    else:
        ra = float('inf')
        a = float('inf')
        t = float('inf')

    output = {"l": l,
              "l_val": l_val,
              "i": i,
              "n": n,
              "n_val": n_val,
              "omega": omega,
              "e": e,
              "e_val": e_val,
              "w": w,
              "theta": theta,
              "rp": rp,
              "ra": ra,
              "a": a,
              "t": t}

    return output


st.sidebar.title("Option Menu", text_alignment="center", anchor=False)

with st.sidebar:
    with st.container(horizontal_alignment="center"):
        divider()
        st.button("Home Page", type="tertiary", on_click=set_option_homepage)
        st.button("Cartesian → Perifocal", type="tertiary", on_click=set_option_cartesian_to_perifocal)

if st.session_state.option == "homepage":
    st.title("AstroTools", anchor=False)
    divider()
    st.write("")

elif st.session_state.option == "cartesian_to_perifocal":
    col1, col2 = st.columns(2)
    with col1:
        st.title("AstroTools", anchor=False)
    with col2:
        st.title("_Cartesian → Perifocal_", anchor=False, text_alignment="right")
    divider()
    st.write("")

    col3, col4 = st.columns([3, 1], border=True)
    
    with col4:
        st.subheader("Import Data (optional)", help="Upload a .csv file in the format of $x, y, z, v_x, v_y, v_z$", anchor=False, text_alignment="center")
        with st.container(horizontal_alignment="center"):
            uploaded_file = st.file_uploader("File Loader", label_visibility="collapsed", type=["csv"], width=120)

    if uploaded_file is not None:
        if st.session_state.last_file != uploaded_file.name:
            df = pd.read_csv(uploaded_file, names=["x", "y", "z", "vx", "vy", "vz"])
            
            st.session_state.cp_x = float(df["x"].iloc[0]) if not pd.isna(df["x"].iloc[0]) else None
            st.session_state.cp_y = float(df["y"].iloc[0]) if not pd.isna(df["y"].iloc[0]) else None
            st.session_state.cp_z = float(df["z"].iloc[0]) if not pd.isna(df["z"].iloc[0]) else None
            st.session_state.cp_vx = float(df["vx"].iloc[0]) if not pd.isna(df["vx"].iloc[0]) else None
            st.session_state.cp_vy = float(df["vy"].iloc[0]) if not pd.isna(df["vy"].iloc[0]) else None
            st.session_state.cp_vz = float(df["vz"].iloc[0]) if not pd.isna(df["vz"].iloc[0]) else None
            
            st.session_state.last_file = uploaded_file.name
    else:
        st.session_state.last_file = None
    
    with col3:
        col5, col6 = st.columns(2, gap="large")
        with col5:
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$μ$**  $(km^3/s^2)$")
                mu_in = st.number_input("mu", value=st.session_state.mu_val, label_visibility="collapsed", placeholder="Insert value")
                st.session_state.mu_val = mu_in

        with col6:
            with st.container(horizontal=True, vertical_alignment="center", horizontal_alignment="distribute"):
                st.button(label="$\mathbf{\mu}_{\mathrm{Earth}}$", type="secondary", width="stretch", on_click=update_mu, args=(398600.0,))
                st.button(label="$\mathbf{\mu}_{\mathrm{Sun}}$", type="secondary", width="stretch", on_click=update_mu, args=(132712440000.0,))
                st.button(label="$\mathbf{\mu}_{\mathrm{Moon}}$", type="secondary", width="stretch", on_click=update_mu, args=(4902.8,))
                st.button(label="$\mathbf{\mu}_{\mathrm{Mars}}$", type="secondary", width="stretch", on_click=update_mu, args=(42828.4,))

        small_divider()
        st.write(" ")

        col7, col8 = st.columns(2, gap="large")
        with col7:
            st.markdown("**Position Vector (km)**")
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$x$**")
                x_in = st.number_input("x", value=st.session_state.cp_x, label_visibility="collapsed", placeholder="Insert value", format="%.4f")
                st.session_state.cp_x = x_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$y$**")
                y_in = st.number_input("y", value=st.session_state.cp_y, label_visibility="collapsed", placeholder="Insert value", format="%.4f")
                st.session_state.cp_y = y_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$z$**")
                z_in = st.number_input("z", value=st.session_state.cp_z, label_visibility="collapsed", placeholder="Insert value", format="%.4f")
                st.session_state.cp_z = z_in
        with col8:
            st.markdown("**Velocity Vector (km/s)**")
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$v_x$**")
                vx_in = st.number_input("vx", value=st.session_state.cp_vx, label_visibility="collapsed", placeholder="Insert value", format="%.4f")
                st.session_state.cp_vx = vx_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$v_y$**")
                vy_in = st.number_input("vy", value=st.session_state.cp_vy, label_visibility="collapsed", placeholder="Insert value", format="%.4f")
                st.session_state.cp_vy = vy_in
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown("**$v_z$**")
                vz_in = st.number_input("vz", value=st.session_state.cp_vz, label_visibility="collapsed", placeholder="Insert value", format="%.4f")
                st.session_state.cp_vz = vz_in

        input_data = [st.session_state.cp_x, st.session_state.cp_y, st.session_state.cp_z,
                      st.session_state.cp_vx, st.session_state.cp_vy, st.session_state.cp_vz,
                      st.session_state.mu_val]
        
    if None not in input_data:  
        divider()
        st.write("")
        with st.container():    
            output = calc_cartesian_to_perifocal(input_data)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Semi-major Axis **($a$)**", f"{output['a']:.2f} km" if output['a'] != float('inf') else "∞", border=True)
            c2.metric("Periapsis Radius ($r_p$)", f"{output['rp']:.2f} km", border=True)
            c3.metric("Apoapsis Radius ($r_a$)", f"{output['ra']:.2f} km" if output['ra'] != float('inf') else "∞", border=True)
            c4.metric("Orbital Period ($T$)", f"{output['t']:.2f} s" if output['t'] != float('inf') else "∞", border=True)
            
            c5, c6, c7, c8 = st.columns(4)
            c5.metric("True Anomaly ($\\theta$)", f"{output['theta']:.2f}°", border=True)
            c6.metric("Inclination ($i$)", f"{output['i']:.2f}°", border=True)
            c7.metric("RAAN ($\Omega$)", f"{output['omega']:.2f}°", border=True)
            c8.metric("Arg. Periapsis ($\omega$)", f"{output['w']:.2f}°", border=True)
            
            c9, c10, c11, c12 = st.columns(4)
            c9.metric("Eccentricity ($e$)", f"{output['e_val']:.4f}", border=True)
            c10.metric("Angular Momentum ($L$)", f"{output['l_val']:.2f} km²/s", border=True)
            c11.metric("Node Line ($N$)", f"{output['n_val']:.2f} km³/s²", border=True)
            c12.write("")
            
            small_divider()
            st.write(" ")
            
            def format_vec(vec, dec=2):
                x, y, z = vec

                return (f"${x:.{dec}f} \\hat{{\\imath}}$"
                        f" ${y:+.{dec}f} \\hat{{\\jmath}}$"
                        f" ${z:+.{dec}f} \\hat{{k}}$")

            c13, c14 = st.columns(2)

            with c13:
                st.metric("Angular Momentum Vector " + r"($\bm{\vec{L}}$)", format_vec(output['l'], 2), border=True)
                st.metric("Node Line Vector " + r"($\bm{\vec{N}}$)", format_vec(output['n'], 2), border=True)
                st.metric("Eccentricity Vector " + r"($\bm{\vec{e}}$)", format_vec(output['e'], 4), border=True)
                st.write("")

            with c14:
                with st.expander("Expand to copy data to clipboard", type="compact"):
                    raw_data = (f"a = {output['a']:.4f}\n"
                                f"e = {output['e_val']:.6f}\n"
                                f"i = {output['i']:.4f}\n"
                                f"omega = {output['omega']:.4f}\n"
                                f"w = {output['w']:.4f}\n"
                                f"theta = {output['theta']:.4f}\n"
                                f"rp = {output['rp']:.4f}\n"
                                f"ra = {output['ra']:.4f}\n"
                                f"t = {output['t']:.4f}\n"
                                f"l_val = {output['l_val']:.4f}\n"
                                f"n_val = {output['n_val']:.4f}\n"
                                f"l_vec = [{output['l'][0]:.4f}, {output['l'][1]:.4f}, {output['l'][2]:.4f}]\n"
                                f"n_vec = [{output['n'][0]:.4f}, {output['n'][1]:.4f}, {output['n'][2]:.4f}]\n"
                                f"e_vec = [{output['e'][0]:.6f}, {output['e'][1]:.6f}, {output['e'][2]:.6f}]")
                    
                    st.code(raw_data, language="python")