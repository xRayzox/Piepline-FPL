import pandas as pd
from datetime import datetime, timezone
import numpy as np
import streamlit as st
import os

# Get the absolute path for the data directory
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

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
# Get the upcoming fixtures for Gameweek 8 and beyond
upcoming_gameweeks = df_fixtures[df_fixtures['finished'] == False]

# Create an empty DataFrame to hold the home/away labels
teams = upcoming_gameweeks['team_a_short'].unique()  # Get unique team short names
unique_gameweeks = upcoming_gameweeks['event'].unique()  # Get unique gameweeks from upcoming games
fdr_matrix = pd.DataFrame(index=teams, columns=unique_gameweeks)  # Create matrix based on unique gameweeks

# Dictionary to store original FDR values for color coding
fdr_values = {}

# Populate the FDR matrix with team names and home/away labels
for index, row in upcoming_gameweeks.iterrows():
    gameweek = row['event']
    team_a = row['team_a_short']
    team_h = row['team_h_short']
    fdr_a = row['team_a_difficulty']  # FDR for team_a
    fdr_h = row['team_h_difficulty']  # FDR for team_h

    # Assign team name with home/away indication
    fdr_matrix.at[team_a, gameweek] = f"{team_h} (A)"  # Team A is playing away
    fdr_matrix.at[team_h, gameweek] = f"{team_a} (H)"  # Team H is playing at home

    # Store FDR values for coloring later
    fdr_values[(team_a, gameweek)] = fdr_a
    fdr_values[(team_h, gameweek)] = fdr_h

# Convert the FDR table to a proper format (e.g., string to prevent confusion with numerical FDR)
fdr_matrix = fdr_matrix.astype(str)

# Define a function to color the DataFrame based on original FDR values
def color_fdr(team, gameweek):
    fdr_value = fdr_values.get((team, gameweek), None)
    
    if fdr_value is None:  # Handle NaN values
        return 'background-color: white;'  # Neutral color for NaN

    # Color coding based on FDR value
    if fdr_value == 1:  # Class for FDR 1
        return 'background-color: #257d5a;'  # Green
    elif fdr_value == 2:  # Class for FDR 2
        return 'background-color: #00ff86;'  # Light Green
    elif fdr_value == 3:  # Class for FDR 3
        return 'background-color: #ebebe4;'  # Yellow
    elif fdr_value == 4:  # Class for FDR 4
        return 'background-color: #ff005a;'  # Orange
    elif fdr_value == 5:  # Class for FDR 5
        return 'background-color: #861d46;'  # Red
    else:
        return ''  # No color for other values

# Create a styled DataFrame to visualize FDR values with color coding
styled_fdr_table = fdr_matrix.copy()  # Copy to apply styles

# Apply color to each cell based on FDR values while retaining team names
def apply_color(row):
    return [color_fdr(row.name, col) for col in row.index]

# Applying the style to the entire DataFrame
styled_fdr_table = styled_fdr_table.style.apply(apply_color, axis=1)
#############################################
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

# Filter fixtures based on the selected gameweek
current_gameweek_fixtures = df_fixtures[df_fixtures['event'] == st.session_state['selected_gameweek']]
grouped_fixtures = current_gameweek_fixtures.groupby('local_date')

# Step 6: Add a radio button to toggle between displays
display_option = st.radio("Select Display", ('Fixture Difficulty Rating', 'Premier League Fixtures'))

if display_option == 'Fixture Difficulty Rating':
    # Title of the FDR table
    st.title('Fantasy Premier League Fixture Difficulty Ratings')
    
    # Display the styled FDR table
    st.write(styled_fdr_table)

elif display_option == 'Premier League Fixtures':
    # Display navigation buttons
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

    # Display the current gameweek title
    st.markdown(f"<h2 style='text-align: center;'>Premier League Fixtures - Gameweek {st.session_state['selected_gameweek']}</h2>", unsafe_allow_html=True)

    # Display grouped fixtures with the date as the title and time for each match
    for date, matches in grouped_fixtures:
        st.markdown(f"<div style='text-align: center;'><strong>🕒 {date}</strong></div>", unsafe_allow_html=True)
        for _, match in matches.iterrows():
            if match['finished']:
                # Display finished matches with the result
                st.markdown(f"""
                    <div style='border: 2px solid #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                        <p style='text-align: center;'><strong>{match['team_h']}</strong> 
                        <span style='color: green;'> {match['team_h_score']} - {match['team_a_score']} </span> 
                        <strong>{match['team_a']}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Display upcoming matches with only the time (local_hour)
                st.markdown(f"""
        <div style='border: 1px solid #ddd; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
            <p style='text-align: center;'>
                <strong>{match['team_h']}</strong> vs <strong>{match['team_a']}</strong>
            </p>
            <p style='text-align: center; color: gray;'>
                Kickoff at {match['local_hour']}
            </p>
        </div>
                """, unsafe_allow_html=True)
