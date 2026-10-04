import streamlit as st
from modules.homepage import main_homepage
from modules.cartesian_to_perifocal import main_cartesian_to_perifocal
from modules.perifocal_to_cartesian import main_perifocal_to_cartesian
from modules.lambert_solver import main_lambert
from auxiliary.custom_visuals import divider

st.set_page_config(page_title="AstroTools", page_icon="assets/astro_tools_logo.png", layout="wide", initial_sidebar_state="expanded")

if "option" not in st.session_state:
    st.session_state.option = "homepage"
if "mu_val" not in st.session_state:
    st.session_state.mu_val = 398600.0
if "last_file" not in st.session_state:
    st.session_state.last_file = None

def set_option(opt):
    st.session_state.option = opt

st.sidebar.title("Option Menu", text_alignment="center", anchor=False)

with st.sidebar:
    with st.container(horizontal_alignment="center"):
        divider()
        st.button("Home Page", type="tertiary", on_click=set_option, args=("homepage",), use_container_width=True)
        st.button("Cartesian → Perifocal", type="tertiary", on_click=set_option, args=("cartesian_to_perifocal",), use_container_width=True)
        st.button("Perifocal → Cartesian", type="tertiary", on_click=set_option, args=("perifocal_to_cartesian",), use_container_width=True)
        st.button("Lambert Problem Solver", type="tertiary", on_click=set_option, args=("lambert",), use_container_width=True)

if st.session_state.option == "homepage":
    main_homepage()

elif st.session_state.option == "cartesian_to_perifocal":
    main_cartesian_to_perifocal()

elif st.session_state.option == "perifocal_to_cartesian":
    main_perifocal_to_cartesian()

elif st.session_state.option == "lambert":
    main_lambert()
