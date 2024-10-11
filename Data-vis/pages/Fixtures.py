import pandas as pd
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

# Add team_a_short and team_h_short columns
df_fixtures['team_a_short'] = df_fixtures['team_a'].map(lambda x: team_short_name_mapping[df_teams[df_teams.team_name == x].id.values[0]] if x in team_name_mapping.values() else None)
df_fixtures['team_h_short'] = df_fixtures['team_h'].map(lambda x: team_short_name_mapping[df_teams[df_teams.team_name == x].id.values[0]] if x in team_name_mapping.values() else None)

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

# Color coding based on FDR values
def color_fdr(fdr_value):
    colors = {
        1: ('#257d5a', 'black'),  # Green
        2: ('#00ff86', 'black'),  # Light Green
        3: ('#ebebe4', 'black'),  # Yellow
        4: ('#ff005a', 'white'),   # Orange
        5: ('#861d46', 'white'),   # Red
    }
    return colors.get(fdr_value, ('white', 'black'))

# Create interactive FDR table
def create_interactive_fdr_table(fdr_matrix):
    for team in fdr_matrix.index:
        cols = st.columns(len(fdr_matrix.columns))
        for i, gameweek in enumerate(fdr_matrix.columns):
            fdr_value = fdr_values.get((team, gameweek), None)
            team_display = fdr_matrix.at[team, gameweek]

            if fdr_value is not None:
                bg_color, font_color = color_fdr(fdr_value)
                cell_html = f"""
                    <div style='border: 1px solid #ccc; padding: 5px; margin: 1px; border-radius: 4px; background-color: {bg_color}; color: {font_color}; cursor: pointer;' 
                         onclick="document.getElementById('selected_fixture').innerText = 'Selected Fixture: {team_display} - FDR: {fdr_value}';">
                        {team_display}
                    </div>
                """
                cols[i].markdown(cell_html, unsafe_allow_html=True)
            else:
                cols[i].markdown(f"<div style='border: 1px solid #ccc; padding: 5px; margin: 1px; border-radius: 4px; background-color: white; color: black;'>{team_display}</div>", unsafe_allow_html=True)

# Streamlit app title
st.title('Fantasy Premier League - Fixture Difficulty Rating')

# Display the FDR matrix
create_interactive_fdr_table(fdr_matrix)

# Selected fixture placeholder
st.markdown("<h4 id='selected_fixture'>Selected Fixture: None</h4>", unsafe_allow_html=True)

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

    current_gameweek_fixtures = df_fixtures[df_fixtures['event'] == st.session_state['selected_gameweek']]
    grouped_fixtures = current_gameweek_fixtures.groupby('local_date')

    for date, matches in grouped_fixtures:
        st.markdown(f"<div style='text-align: center;'><strong>🕒 {date}</strong></div>", unsafe_allow_html=True)
        for _, match in matches.iterrows():
            if match['finished']:
                st.markdown(f"<p style='text-align: center;'><strong>{match['team_h']}</strong> <span style='color: green;'> {int(match['team_h_score'])} - {int(match['team_a_score'])} </span> <strong>{match['team_a']}</strong></p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='text-align: center;'> <strong>{match['team_h']}</strong> vs <strong>{match['team_a']}</strong> - Kickoff at {match['local_hour']}</p>", unsafe_allow_html=True)

# Run the Streamlit application
if __name__ == "__main__":
    st.run()
