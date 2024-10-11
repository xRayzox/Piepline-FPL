
# app.py
import streamlit as st
import fixture
import Hello


st.title("My Multi-Page Streamlit App")
st.sidebar.title("Navigation")

# Create a sidebar for navigation
pages = {
    "hello": Hello,
    "fixture": fixture,
}

# Select a page from the sidebar
selection = st.sidebar.selectbox("Select a page:", list(pages.keys()))

# Display the selected page
page = pages[selection]
page.app()  # Call the app function from the respective page module
