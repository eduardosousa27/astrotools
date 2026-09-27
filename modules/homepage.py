import streamlit as st
import plotly.graph_objects as go
from numpy import array, inner, cross, clip, degrees, sin, cos, arcsin, arccos, arctan2, sqrt, pi, linspace, radians
from numpy.linalg import norm
import pandas as pd
from auxiliary.custom_visuals import divider, small_divider
from auxiliary.global_calculations import update_mu

def main_homepage():
    st.title("AstroTools", anchor=False)
    divider()
    st.write("")

    with st.columns([1, 4, 1])[1]:
        st.subheader("Welcome!", text_alignment="center")
        st.text("This is AstroTools, an app that can help you compute various orbital parameters in a simple and intuitive way. " \
        "Feel free to explore the various functions of the app by choosing an option in the sidebar. " \
        "You can jump between the various options and your progress will not be erased in each one. " \
        "The gravitational parameter μ caries over across all tabs, and you can change it anytime you want.", text_alignment="justify")