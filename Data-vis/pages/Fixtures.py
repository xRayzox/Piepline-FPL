import pandas as pd
from datetime import datetime, timezone
import numpy as np
import streamlit as st
import os

# Get the absolute path for the data directory
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

df_fact_player = pd.read_csv(os.path.join(data_dir, 'Fact_Player.csv'))
df_gameweeks = pd.read_csv(os.path.join(data_dir, 'Gameweeks.csv'))
df_player_history = pd.read_csv(os.path.join(data_dir, 'Player_history.csv'))
df_players = pd.read_csv(os.path.join(data_dir, 'Players.csv'))
df_positions = pd.read_csv(os.path.join(data_dir, 'Positions.csv'))
df_teams = pd.read_csv(os.path.join(data_dir, 'Teams.csv'))
df_fixtures = pd.read_csv(os.path.join(data_dir, 'Fixtures.csv'))

# Create mappings of team IDs to team names and short names
team_name_mapping = pd.Series(df_teams.team_name.values, index=df_teams.id).to_dict()
team_short_name_mapping = pd.Series(df_teams.short_name.values, index=df_teams.id).to_dict()

# Replace team_a and team_h IDs with team names
df_fixtures['team_a'] = df_fixtures['team_a'].replace(team_name_mapping)
df_fixtures['team_h'] = df_fixtures['team_h'].replace(team_name_mapping)

# Add team_a_short and team_h_short columns using the original team IDs
df_fixtures['team_a_short'] = df_fixtures['team_a'].map(lambda x: team_short_name_mapping[df_teams[df_teams.team_name == x].id.values[0]] if x in team_name_mapping.values() else None)
df_fixtures['team_h_short'] = df_fixtures['team_h'].map(lambda x: team_short_name_mapping[df_teams[df_teams.team_name == x].id.values[0]] if x in team_name_mapping.values() else None)
df_fixtures = df_fixtures.drop(columns=['pulse_id'])

# Step 1: Prepare the Data for FDR Table
# Get upcoming gameweeks
upcoming_gameweeks = df_fixtures[df_fixtures['finished'] == False]

# Create an empty DataFrame to hold the display values
teams = upcoming_gameweeks['team_a_short'].unique()  # Get unique team short names
unique_gameweeks = upcoming_gameweeks['event'].unique()  # Get unique gameweeks from upcoming games

# Format gameweek numbers with 'GW' prefix
formatted_gameweeks = [f'GW{gw}' for gw in unique_gameweeks]

# Create a matrix based on unique gameweeks
fdr_matrix = pd.DataFrame(index=teams, columns=formatted_gameweeks)

# Dictionary to store original FDR values for color coding
fdr_values = {}

# Populate the FDR matrix with display values and keep track of FDR values
for index, row in upcoming_gameweeks.iterrows():
    gameweek = f'GW{row["event"]}'  # Format gameweek with 'GW'
    team_a = row['team_a_short']
    team_h = row['team_h_short']
    fdr_a = row['team_a_difficulty']  # FDR for team_a
    fdr_h = row['team_h_difficulty']  # FDR for team_h

    # Assign home/away display values to the matrix with tooltips
    fdr_matrix.at[team_a, gameweek] = f"<span title='FDR: {fdr_a}'>{team_h} (A)</span>"  # Team A is playing away
    fdr_matrix.at[team_h, gameweek] = f"<span title='FDR: {fdr_h}'>{team_a} (H)</span>"  # Team H is playing at home

    # Store FDR values for coloring later
    fdr_values[(team_a, gameweek)] = fdr_a
    fdr_values[(team_h, gameweek)] = fdr_h

# Convert the FDR table to a proper format (e.g., string to prevent confusion with numerical FDR)
fdr_matrix = fdr_matrix.astype(str)

# Define a function to color the DataFrame based on original FDR values
def color_fdr(team, gameweek):
    fdr_value = fdr_values.get((team, gameweek), None)
    
    if fdr_value is None:  # Handle NaN values
        return 'background-color: white; color: black;'  # Neutral color for NaN

    # Color coding based on FDR value
    colors = {
        1: ('#257d5a', 'black'),  # Green
        2: ('#00ff86', 'black'),  # Light Green
        3: ('#ebebe4', 'black'),  # Yellow
        4: ('#ff005a', 'white'),   # Orange
        5: ('#861d46', 'white'),   # Red
    }

    bg_color, font_color = colors.get(fdr_value, ('white', 'black'))
    return f'background-color: {bg_color}; color: {font_color};'

# Create a styled DataFrame to visualize FDR values with color coding
styled_fdr_table = fdr_matrix.copy()  # Copy to apply styles

# Apply color to each cell based on FDR values while retaining the display values
styled_fdr_table = styled_fdr_table.style.apply(lambda row: [color_fdr(row.name, col) for col in row.index], axis=1)

# Add gameweek data
df_fixtures['datetime'] = pd.to_datetime(df_fixtures['kickoff_time'], utc=True)
df_fixtures['local_time'] = df_fixtures['datetime'].dt.tz_convert('Europe/London').dt.strftime('%A %d %B %Y %H:%M')
df_fixtures['local_date'] = df_fixtures['datetime'].dt.tz_convert('Europe/London').dt.strftime('%A %d %B %Y')
df_fixtures['local_hour'] = df_fixtures['datetime'].dt.tz_convert('Europe/London').dt.strftime('%H:%M')

# Get the unique gameweeks and next gameweek
gameweeks = sorted(df_fixtures['event'].unique())
next_gameweek = next(
    (gw for gw in gameweeks if df_fixtures[(df_fixtures['event'] == gw) & (df_fixtures['finished'] == False)].shape[0] > 0),
    gameweeks[0]  # fallback to first gameweek if all are finished
)

# Initialize session state to keep track of the current gameweek
if 'selected_gameweek' not in st.session_state:
    st.session_state['selected_gameweek'] = next_gameweek

# Initialize session state for the selected display option
if 'display_option' not in st.session_state:
    st.session_state['display_option'] = 'Fixture Difficulty Rating'

# Step 6: Add a radio button to toggle between displays
st.title('Fantasy Premier League')

display_option = st.radio("Select Display", ('Fixture Difficulty Rating', 'Premier League Fixtures'), index=0)

# Update session state when the display option changes
st.session_state['display_option'] = display_option

# Filter fixtures based on the selected gameweek
current_gameweek_fixtures = df_fixtures[df_fixtures['event'] == st.session_state['selected_gameweek']]
grouped_fixtures = current_gameweek_fixtures.groupby('local_date')

# Handle display option
if st.session_state['display_option'] == 'Fixture Difficulty Rating':
    st.write(styled_fdr_table)

elif st.session_state['display_option'] == 'Premier League Fixtures':
    st.markdown("<h3 style='text-align: center;'>Gameweek Navigation</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    if col1.button("⬅️ Previous"):
        current_index = gameweeks.index(st.session_state['selected_gameweek'])
        if current_index > 0:
            st.session_state['selected_gameweek'] = gameweeks[current_index - 1]

    if col3.button("➡️ Next"):
        current_index = gameweeks.index(st.session_state['selected_gameweek'])
        if current_index < len(gameweeks) - 1:
            st.session_state['selected_gameweek'] = gameweeks[current_index + 1]

    st.markdown(f"<h2 style='text-align: center;'>Premier League Fixtures - Gameweek {st.session_state['selected_gameweek']}</h2>", unsafe_allow_html=True)

    # Display grouped fixtures with the date as the title and time for each match
    for date, matches in grouped_fixtures:
        st.markdown(f"<div style='text-align: center;'><strong>🕒 {date}</strong></div>", unsafe_allow_html=True)
        for _, match in matches.iterrows():
            if match['finished']:
                # Display finished matches with the result
                st.markdown(f"""
                    <div style='border: 2px solid #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px; background-color: #f9f9f9;'>
                        <p style='text-align: center;'>
                            <strong>{match['team_h']}</strong> 
                            <span style='color: gray;'>({match['local_hour']})</span> 
                            - 
                            <strong>{match['team_a']}</strong>
                        </p>
                        <p style='text-align: center; font-size: 14px; color: gray;'>
                            Result: {match['team_h_score']} - {match['team_a_score']}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Display upcoming matches
                st.markdown(f"""
                    <div style='border: 2px solid #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px; background-color: #f9f9f9;'>
                        <p style='text-align: center;'>
                            <strong>{match['team_h']}</strong> 
                            <span style='color: gray;'>({match['local_hour']})</span> 
                            - 
                            <strong>{match['team_a']}</strong>
                        </p>
                    </div>
                """, unsafe_allow_html=True)

# Footer with additional information
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Data sourced from Fantasy Premier League API.</p>", unsafe_allow_html=True)
