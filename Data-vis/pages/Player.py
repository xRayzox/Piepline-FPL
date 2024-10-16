import streamlit as st
import pandas as pd
import os

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
# Load your FPL data
df_teams = pd.read_csv(os.path.join(data_dir, "Teams.csv"))
df_fixtures = pd.read_csv(os.path.join(data_dir, "Fixtures.csv"))
df_fact_player = pd.read_csv(os.path.join(data_dir, "Fact_Player.csv"))
df_gameweeks = pd.read_csv(os.path.join(data_dir, "Gameweeks.csv"))
df_player_history = pd.read_csv(os.path.join(data_dir, "Player_history.csv"))
df_players = pd.read_csv(os.path.join(data_dir, "Players.csv"))
df_positions = pd.read_csv(os.path.join(data_dir, "Positions.csv"))

# Function to filter players based on selected metrics
def filter_players(players_df, metrics):
    # Implement your filtering logic here based on selected metrics
    return players_df  # Placeholder return

# Streamlit layout
st.title("Fantasy Premier League Player Selection Tool")

# Select maximum players per club
max_players = st.number_input("Max players/club", min_value=1, max_value=5, value=3)

# Include injured/suspended players
include_injured = st.checkbox("Include injured/suspended players")

# Select Gameweek
gameweek = st.number_input("Gameweek", min_value=1, value=8)

# Metric selection
metrics = st.multiselect("Select metrics to include", [
    "Dreamteam Count", "Form", "Points per game", "Selected by %",
    "Goals scored", "Assists", "Minutes played", "ICT Index",
    "Creativity", "Threat", "Influence", "Clean sheets", "Goals conceded",
    "Yellow cards", "Red cards", "xG", "xA", "xG/90", "xA/90",
    "xGI/90", "xGI", "xGC/90", "xGC", "Fixture difficulty (5)",
    "Fixture difficulty (1)", "Fixture difficulty (2)", "Fixture difficulty (10)",
    "Price", "Transfers in", "Transfers out", "Median points per game",
    "Median BPS"
])

# Drop metric sections for each position
for position in ['Forward', 'Midfield', 'Defence']:
    st.subheader(f"{position} Metrics")
    drop_metric_max = st.selectbox(f"Drop metric to maximise {position}", metrics)
    drop_metric_min = st.selectbox(f"Drop metric to minimise {position}", metrics)

# Build button
if st.button("Build ⚽️"):
    filtered_players = filter_players(players_df, metrics)
    st.write("Selected Players:")
    st.dataframe(filtered_players)

