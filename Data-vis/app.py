import streamlit as st

# Create a sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page:", ["Home", "Fixtures"])

# Show different pages based on selection
if page == "Home":
    st.title("My Multi-Page Streamlit App")
    st.write("Welcome to the multi-page app!")
elif page == "Fixtures":
    import fixture  # Import your page1.py
