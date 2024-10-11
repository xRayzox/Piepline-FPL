# app.py
import streamlit as st

st.title("My Multi-Page Streamlit App")
st.sidebar.title("Navigation")

# Create a sidebar for navigation
pages = ["Home", "Analysis", "Settings"]
choice = st.sidebar.selectbox("Select a page:", pages)

if choice == "Home":
    st.write("Welcome to the Home Page!")
elif choice == "Analysis":
    st.write("This is the Analysis Page.")
elif choice == "Settings":
    st.write("This is the Settings Page.")
