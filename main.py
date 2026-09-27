import streamlit as st
from modules.homepage import main_homepage
from modules.cartesian_to_perifocal import main_cartesian_to_perifocal
from modules.perifocal_to_cartesian import main_perifocal_to_cartesian
from auxiliary.custom_visuals import divider

st.set_page_config(page_title="AstroTools", page_icon="assets/astro_tools_logo.png", layout="wide", initial_sidebar_state="expanded")

if "option" not in st.session_state:
    st.session_state.option = "homepage"
if "mu_val" not in st.session_state:
    st.session_state.mu_val = 398600.0
if "last_file" not in st.session_state:
    st.session_state.last_file = None

def set_option_homepage():
    st.session_state.option = "homepage"

def set_option_cartesian_to_perifocal():
    st.session_state.option = "cartesian_to_perifocal"

def set_option_perifocal_to_cartesian():
    st.session_state.option = "perifocal_to_cartesian"

st.sidebar.title("Option Menu", text_alignment="center", anchor=False)

with st.sidebar:
    with st.container(horizontal_alignment="center"):
        divider()
        st.button("Home Page", type="tertiary", on_click=set_option_homepage)
        st.button("Cartesian → Perifocal", type="tertiary", on_click=set_option_cartesian_to_perifocal)
        st.button("Perifocal → Cartesian", type="tertiary", on_click=set_option_perifocal_to_cartesian)

if st.session_state.option == "homepage":
    main_homepage()

elif st.session_state.option == "cartesian_to_perifocal":
    main_cartesian_to_perifocal()

elif st.session_state.option == "perifocal_to_cartesian":
    main_perifocal_to_cartesian()
