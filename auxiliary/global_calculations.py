from streamlit import session_state

def update_mu(val):
    session_state.mu_val = val