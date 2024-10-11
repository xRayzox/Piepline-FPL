import streamlit as st
from multipage import MultiPage
from pages import fixture, Hello  # Import your page modules

app = MultiPage()

# Add all pages here
app.add_page("Fixtures", fixture.app)
app.add_page("hello", Hello.app)

app.run()