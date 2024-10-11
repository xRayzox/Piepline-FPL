import streamlit as st

# Create a sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page:", ["Home", "Page 1", "Page 2"])

# Show different pages based on selection
if page == "Home":
    st.title("My Multi-Page Streamlit App")
    st.write("Welcome to the multi-page app!")
elif page == "Page 1":
    import pages.fixture  # Import your page1.py
elif page == "Page 2":
    import pages.Hello  # Import your page2.py
