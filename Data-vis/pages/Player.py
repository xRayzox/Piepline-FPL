import pandas as pd
from datetime import datetime, timezone
import numpy as np
import streamlit as st
import plotly.express as px
import os

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

# Load all CSV files
df_teams = pd.read_csv(os.path.join(data_dir, "Teams.csv"))
df_fixtures = pd.read_csv(os.path.join(data_dir, "Fixtures.csv"))
df_fact_player = pd.read_csv(os.path.join(data_dir, "Fact_Player.csv"))
df_gameweeks = pd.read_csv(os.path.join(data_dir, "Gameweeks.csv"))
df_player_history = pd.read_csv(os.path.join(data_dir, "Player_history.csv"))
df_players = pd.read_csv(os.path.join(data_dir, "Players.csv"))
df_positions = pd.read_csv(os.path.join(data_dir, "Positions.csv"))


# Merge DataFrames with correct column names based on your schema
df_merged = (
    df_fact_player
    .merge(df_players, left_on='element', right_on='id', suffixes=('', '_player'))
    .merge(df_positions, left_on='element_type', right_on='id', suffixes=('', '_position'))
    .merge(df_teams, left_on='team', right_on='id', suffixes=('', '_team'))
    .merge(df_gameweeks, left_on='GW', right_on='id', suffixes=('', '_gameweek'))
)

import matplotlib.pyplot as plt


st.title("Player Performance Scatter Plot")

# Scatter plot using Matplotlib
plt.figure(figsize=(10, 6))
plt.scatter(df_merged['price'], df_merged['total_points'], color='blue', alpha=0.5)

# Adding labels and title
plt.title('Player Performance: Cost vs Total Points')
plt.xlabel('Cost')
plt.ylabel('Total Points')

# Annotate players
for i, player in enumerate(df_merged['web_name']):
    plt.annotate(player, (df_merged['price'][i], df_merged['total_points'][i]), textcoords="offset points", xytext=(0,10), ha='center')

# Display plot in Streamlit
plt
st.pyplot(plt)


st.title("Player Performance Scatter Plot")

# Scatter plot using Plotly
fig = px.scatter(df_merged, x='price', y='total_points', text='web_name', title='Player Performance: Cost vs Total Points')
fig.update_traces(textposition='top center')  # Position text labels
fig.update_layout(xaxis_title='Cost', yaxis_title='Total Points')

# Display plot in Streamlit
st.plotly_chart(fig)