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


# Step 1: Prepare the Data
# Get the upcoming fixtures for Gameweek 8 and beyond
upcoming_gameweeks = df_fixtures[df_fixtures['finished'] == False]

# Initialize a list to hold the FDR records
fdr_records = []

# Iterate over each fixture to assign FDR
for index, row in upcoming_gameweeks.iterrows():
    # Assign difficulty based on team_a and team_h
    team_a = row['team_a']
    team_a_short = row['team_a_short']  # Get the short name for team_a
    team_h = row['team_h']
    team_h_short = row['team_h_short']  # Get the short name for team_h
    
    # Create a record for team_a
    fdr_records.append({
        'Team': team_a_short,  # Use the short name for display
        'Gameweek': row['event'],
        'FDR': row['team_a_difficulty']
    })

    # Create a record for team_h
    fdr_records.append({
        'Team': team_h_short,  # Use the short name for display
        'Gameweek': row['event'],
        'FDR': row['team_h_difficulty']
    })

# Step 2: Create a DataFrame from the records
fdr_results = pd.DataFrame(fdr_records)

# Step 3: Pivot the DataFrame to create the FDR table
fdr_table = fdr_results.pivot(index='Team', columns='Gameweek', values='FDR')

# Step 4: Define a function to color the DataFrame based on FDR values
def color_fdr(val):
    if pd.isna(val):  # Handle NaN values
        return 'background-color: white;'  # Neutral color for NaN
    elif val == 1:  # Class for FDR 1
        return 'background-color: #257d5a;'  # Green
    elif val == 2:  # Class for FDR 2
        return 'background-color: #00ff86;'  # Light Green
    elif val == 3:  # Class for FDR 3
        return 'background-color: #ebebe4;'  # Yellow
    elif val == 4:  # Class for FDR 4
        return 'background-color: #ff005a;'  # Orange
    elif val == 5:  # Class for FDR 5
        return 'background-color: #861d46;'  # Red
    else:
        return ''  # No color for other values

# Step 5: Apply the color function to the DataFrame using applymap
styled_fdr_table = fdr_table.style.applymap(color_fdr)

# Title of the app
st.title('Fantasy Premier League Fixture Difficulty Ratings')

# Display the styled table
st.write(styled_fdr_table)


###################
# Create mappings of team IDs to team names
team_name_mapping = pd.Series(df_teams.team_name.values, index=df_teams.id).to_dict()

# Replace team_a and team_h IDs with team names
df_fixtures['team_a'] = df_fixtures['team_a'].replace(team_name_mapping)
df_fixtures['team_h'] = df_fixtures['team_h'].replace(team_name_mapping)

# Add a 'datetime' column by converting the 'kickoff_time' to datetime format
df_fixtures['datetime'] = pd.to_datetime(df_fixtures['kickoff_time'], utc=True)

# Extract the local time for display
df_fixtures['local_time'] = df_fixtures['datetime'].dt.tz_convert('Europe/London').dt.strftime('%A %d %B %Y %H:%M')

# Separate date and time
df_fixtures['local_date'] = df_fixtures['datetime'].dt.tz_convert('Europe/London').dt.strftime('%A %d %B %Y')
df_fixtures['local_hour'] = df_fixtures['datetime'].dt.tz_convert('Europe/London').dt.strftime('%H:%M')

# Get the unique gameweeks
gameweeks = sorted(df_fixtures['event'].unique())

# Find the next gameweek that is not completely finished
next_gameweek = next(
    (gw for gw in gameweeks if df_fixtures[(df_fixtures['event'] == gw) & (df_fixtures['finished'] == False)].shape[0] > 0),
    gameweeks[0]  # fallback to first gameweek if all are finished
)

# Step 1: Initialize session state to keep track of the current gameweek
if 'selected_gameweek' not in st.session_state:
    st.session_state['selected_gameweek'] = next_gameweek

# Step 2: Add buttons to navigate between gameweeks
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

# Step 3: Filter the fixtures based on the selected gameweek
current_gameweek_fixtures = df_fixtures[df_fixtures['event'] == st.session_state['selected_gameweek']]

# Step 4: Group fixtures by date (local_date) and display each match by time (local_hour)
grouped_fixtures = current_gameweek_fixtures.groupby('local_date')

# Step 5: Display grouped fixtures with the date as the title and time for each match
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

# Display navigation and gameweek info
st.markdown(f"<p style='text-align: center;'>Gameweek {st.session_state['selected_gameweek']} of {max(gameweeks)}</p>", unsafe_allow_html=True)