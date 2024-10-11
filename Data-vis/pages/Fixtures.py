import pandas as pd
from datetime import datetime, timezone
import numpy as np
import streamlit as st
import os

# Get the absolute path for the data directory
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

# Load DataFrames (using sample data for demonstration)
df_fact_player = pd.read_csv(os.path.join(data_dir, 'Fact_Player.csv'))
df_gameweeks = pd.read_csv(os.path.join(data_dir, 'Gameweeks.csv'))
df_player_history = pd.read_csv(os.path.join(data_dir, 'Player_history.csv'))
df_players = pd.read_csv(os.path.join(data_dir, 'Players.csv'))
df_positions = pd.read_csv(os.path.join(data_dir, 'Positions.csv'))
df_teams = pd.read_csv(os.path.join(data_dir, 'Teams.csv'))
df_fixtures = pd.read_csv(os.path.join(data_dir, 'Fixtures.csv'))

# Data Preprocessing
team_name_mapping = pd.Series(df_teams.team_name.values, index=df_teams.id).to_dict()
team_short_name_mapping = pd.Series(df_teams.short_name.values, index=df_teams.id).to_dict()
df_fixtures['team_a'] = df_fixtures['team_a'].replace(team_name_mapping)
df_fixtures['team_h'] = df_fixtures['team_h'].replace(team_name_mapping)
df_fixtures['team_a_short'] = df_fixtures['team_a'].map(lambda x: team_short_name_mapping[df_teams[df_teams.team_name == x].id.values[0]] if x in team_name_mapping.values() else None)
df_fixtures['team_h_short'] = df_fixtures['team_h'].map(lambda x: team_short_name_mapping[df_teams[df_teams.team_name == x].id.values[0]] if x in team_name_mapping.values() else None)
df_fixtures = df_fixtures.drop(columns=['pulse_id'])

# Add datetime columns
df_fixtures['datetime'] = pd.to_datetime(df_fixtures['kickoff_time'], utc=True)
df_fixtures['local_time'] = df_fixtures['datetime'].dt.tz_convert('Europe/London').dt.strftime('%A %d %B %Y %H:%M')
df_fixtures['local_date'] = df_fixtures['datetime'].dt.tz_convert('Europe/London').dt.strftime('%A %d %B %Y')
df_fixtures['local_hour'] = df_fixtures['datetime'].dt.tz_convert('Europe/London').dt.strftime('%H:%M')

# FDR Matrix Calculation
upcoming_gameweeks = df_fixtures[df_fixtures['finished'] == False]
teams = upcoming_gameweeks['team_a_short'].unique()
unique_gameweeks = upcoming_gameweeks['event'].unique()
formatted_gameweeks = [f'GW{gw}' for gw in unique_gameweeks]
fdr_matrix = pd.DataFrame(index=teams, columns=formatted_gameweeks)
fdr_values = {}

for index, row in upcoming_gameweeks.iterrows():
    gameweek = f'GW{row["event"]}'
    team_a = row['team_a_short']
    team_h = row['team_h_short']
    fdr_a = row['team_a_difficulty']
    fdr_h = row['team_h_difficulty']

    fdr_matrix.at[team_a, gameweek] = f"{team_h} (A)"
    fdr_matrix.at[team_h, gameweek] = f"{team_a} (H)"
    fdr_values[(team_a, gameweek)] = fdr_a
    fdr_values[(team_h, gameweek)] = fdr_h

fdr_matrix = fdr_matrix.astype(str)

# Color Coding Function
def color_fdr(team, gameweek):
    fdr_value = fdr_values.get((team, gameweek), None)
    colors = {
        1: ('#257d5a', 'black'), 
        2: ('#00ff86', 'black'),  
        3: ('#ebebe4', 'black'), 
        4: ('#ff005a', 'white'),  
        5: ('#861d46', 'white'),   
    }
    bg_color, font_color = colors.get(fdr_value, ('white', 'black'))
    return f'background-color: {bg_color}; color: {font_color};'

styled_fdr_table = fdr_matrix.style.apply(lambda row: [color_fdr(row.name, col) for col in row.index], axis=1)

# --- Streamlit App ---
st.title('Fantasy Premier League Dashboard')

# Sidebar for Navigation
st.sidebar.title("Navigation")
selected_page = st.sidebar.radio("Go to", ["FDR & Fixtures", "Player Stats"])

# Global Gameweek Selection
gameweeks = sorted(df_fixtures['event'].unique())
next_gameweek = next(
    (gw for gw in gameweeks if df_fixtures[(df_fixtures['event'] == gw) & (df_fixtures['finished'] == False)].shape[0] > 0),
    gameweeks[0] 
)

if 'selected_gameweek' not in st.session_state:
    st.session_state['selected_gameweek'] = next_gameweek

st.sidebar.markdown("### Gameweek Selection")
st.session_state['selected_gameweek'] = st.sidebar.selectbox(
    "Select Gameweek:", gameweeks, index=gameweeks.index(st.session_state['selected_gameweek'])
)

# Page 1: FDR & Fixtures
if selected_page == "FDR & Fixtures":
    st.markdown("<h2 style='text-align: center;'>Fixture Difficulty Rating</h2>", unsafe_allow_html=True)
    st.write(styled_fdr_table)

    st.markdown("<h2 style='text-align: center;'>Premier League Fixtures</h2>", unsafe_allow_html=True)

    # Filter fixtures based on the selected gameweek
    current_gameweek_fixtures = df_fixtures[df_fixtures['event'] == st.session_state['selected_gameweek']]
    grouped_fixtures = current_gameweek_fixtures.groupby('local_date')

    for date, matches in grouped_fixtures:
        st.markdown(f"<div style='text-align: center;'><strong>🕒 {date}</strong></div>", unsafe_allow_html=True)
        for _, match in matches.iterrows():
            if match['finished']:
                st.markdown(f"""
                    <div style='border: 2px solid #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px; background-color: #f9f9f9;'>
                        <p style='text-align: center;'>
                            <strong>{match['team_h']}</strong> 
                            <span style='color: green;'> 
                                {int(match['team_h_score'])} - {int(match['team_a_score'])}
                            </span> 
                            <strong>{match['team_a']}</strong>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style='border: 1px solid #ddd; padding: 10px; border-radius: 5px; margin-bottom: 10px; background-color: #f0f0f0;'>
                        <p style='text-align: center;'>
                            <strong>{match['team_h']}</strong> vs <strong>{match['team_a']}</strong>
                        </p>
                        <p style='text-align: center; color: gray;'>
                            Kickoff at {match['local_hour']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

# Page 2: Player Stats (Example: Top Goal Scorers)
elif selected_page == "Player Stats":
    st.markdown("<h2 style='text-align: center;'>Player Stats</h2>", unsafe_allow_html=True)

    # Example: Show top goal scorers for the selected gameweek
    top_scorers = df_fact_player[df_fact_player['gameweek'] == st.session_state['selected_gameweek']].nlargest(10, 'goals_scored')
    top_scorers = top_scorers.merge(df_players[['id', 'name']], left_on='player_id', right_on='id') 

    st.write(f"Top 10 Goal Scorers for Gameweek {st.session_state['selected_gameweek']}")
    st.table(top_scorers[['name', 'goals_scored']])  