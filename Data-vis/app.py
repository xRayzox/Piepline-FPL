# app.py
import streamlit as st
from pages import fixture, Hello  # Import your page modules

# Set page configuration
st.set_page_config(page_title="FPL App", page_icon="⚽", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Fixture"])

# Render the appropriate page based on user selection
if page == "Home":
    Hello.app()  # Call the function in hello.py
elif page == "Fixture" : 
    fixture.app()  # Call the function in fixture.py
