import pandas as pd
from datetime import datetime, timezone
import numpy as np
import streamlit as st
import os

# Get the absolute path for the data directory
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

# Load CSV files
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

# Prepare Data for FDR Table
upcoming_gameweeks = df_fixtures[df_fixtures['finished'] == False]
teams = upcoming_gameweeks['team_a_short'].unique()
unique_gameweeks = upcoming_gameweeks['event'].unique()

# Format gameweek numbers with 'GW' prefix
formatted_gameweeks = [f'GW{gw}' for gw in unique_gameweeks]

# Create a matrix based on unique gameweeks
fdr_matrix = pd.DataFrame(index=teams, columns=formatted_gameweeks)
fdr_values = {}

# Populate the FDR matrix
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

# Define a function to color the DataFrame based on original FDR values
def color_fdr(team, gameweek):
    fdr_value = fdr_values.get((team, gameweek), None)
    
    if fdr_value is None:
        return 'background-color: white; color: black;'
    
    colors = {
        1: ('#257d5a', 'black'),  # Green
        2: ('#00ff86', 'black'),  # Light Green
        3: ('#ebebe4', 'black'),  # Yellow
        4: ('#ff005a', 'white'),   # Orange
        5: ('#861d46', 'white'),   # Red
    }

    bg_color, font_color = colors.get(fdr_value, ('white', 'black'))
    return f'background-color: {bg_color}; color: {font_color};'

# Function to create interactive FDR table
def create_interactive_fdr_table(fdr_matrix):
    # Create a placeholder for the FDR table
    fdr_placeholder = st.empty()

    # Display the FDR matrix
    for team in fdr_matrix.index:
        row_html = ""
        for gameweek in fdr_matrix.columns:
            fdr_value = fdr_values.get((team, gameweek), None)
            team_display = fdr_matrix.at[team, gameweek]
            if fdr_value is not None:
                color_code = color_fdr(team, gameweek)
                tooltip = f"{team_display} - FDR: {fdr_value}"
                cell_html = f"""
                    <div style='display: inline-block; border: 1px solid #ccc; padding: 5px; margin: 1px; border-radius: 4px; {color_code}'>
                        <span title="{tooltip}" style="cursor: pointer;" onclick="handleCellClick('{team}', '{gameweek}')">{team_display}</span>
                    </div>
                """
            else:
                cell_html = f"<div style='display: inline-block; border: 1px solid #ccc; padding: 5px; margin: 1px; border-radius: 4px; background-color: white; color: black;'>{team_display}</div>"

            row_html += cell_html
        fdr_placeholder.markdown(f"<div style='display: flex; justify-content: center;'>{row_html}</div>", unsafe_allow_html=True)

# Add the FDR table to the Streamlit app
st.title('Fantasy Premier League - Fixture Difficulty Rating')
create_interactive_fdr_table(fdr_matrix)

# Initialize session state for selected fixture
if 'selected_fixture' not in st.session_state:
    st.session_state['selected_fixture'] = None

# Optionally, display details for a specific fixture when clicked
if st.session_state['selected_fixture']:
    selected_team, selected_gameweek = st.session_state['selected_fixture']
    # Fetch and display detailed info for the selected fixture here
    st.write(f"Details for {selected_team} in {selected_gameweek}:")
    # Add further information retrieval and display logic here

# Handle gameweek navigation
df_fixtures['datetime'] = pd.to_datetime(df_fixtures['kickoff_time'], utc=True)
df_fixtures['local_time'] = df_fixtures['datetime'].dt.tz_convert('Europe/London').dt.strftime('%A %d %B %Y %H:%M')
df_fixtures['local_date'] = df_fixtures['datetime'].dt.tz_convert('Europe/London').dt.strftime('%A %d %B %Y')
df_fixtures['local_hour'] = df_fixtures['datetime'].dt.tz_convert('Europe/London').dt.strftime('%H:%M')

gameweeks = sorted(df_fixtures['event'].unique())
next_gameweek = next(
    (gw for gw in gameweeks if df_fixtures[(df_fixtures['event'] == gw) & (df_fixtures['finished'] == False)].shape[0] > 0),
    gameweeks[0]
)

# Initialize session state to keep track of the current gameweek
if 'selected_gameweek' not in st.session_state:
    st.session_state['selected_gameweek'] = next_gameweek

# Radio button for display option
display_option = st.radio("Select Display", ('Fixture Difficulty Rating', 'Premier League Fixtures'), index=0)

# Filter fixtures based on the selected gameweek
current_gameweek_fixtures = df_fixtures[df_fixtures['event'] == st.session_state['selected_gameweek']]
grouped_fixtures = current_gameweek_fixtures.groupby('local_date')

# Handle display option
if display_option == 'Fixture Difficulty Rating':
    create_interactive_fdr_table(fdr_matrix)

elif display_option == 'Premier League Fixtures':
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
                st.write(f"{match['team_h']} vs {match['team_a']} - {match['local_hour']} (Finished)")
            else:
                st.write(f"{match['team_h']} vs {match['team_a']} - {match['local_hour']} (Upcoming)")

# Run the Streamlit application
if __name__ == "__main__":
    st.run()
