from streamlit import markdown

def divider():
    markdown("""<div style="height: 1px;
                background-color: #21c647;
                border-radius: 999px;
                margin: 1rem 0; "></div>""",
                unsafe_allow_html=True)

def small_divider():
    markdown("""<div style="height: 0.5px;
                background-color: #696969;
                border-radius: 999px;
                margin: 0rem 0; "></div>""",
                unsafe_allow_html=True)