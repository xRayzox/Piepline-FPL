import pandas as pd
from datetime import datetime, timezone
import numpy as np
import streamlit as st


# Load all CSV files
df_fact_player = pd.read_csv('../data/Fact_Player.csv')
df_gameweeks = pd.read_csv('../data/Gameweeks.csv')
df_player_history = pd.read_csv('../data/Player_history.csv')
df_players = pd.read_csv('../data/Players.csv')
df_positions = pd.read_csv('../data/Positions.csv')
df_teams = pd.read_csv('../data/Teams.csv')
df_fixtures=pd.read_csv('../data/Fixtures.csv')

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