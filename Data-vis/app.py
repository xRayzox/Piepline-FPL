import pandas as pd
import numpy as np
import streamlit as st
import os

# Function to load data
@st.cache_data
def load_data(data_dir):
    return {
        'df_fact_player': pd.read_csv(os.path.join(data_dir, 'Fact_Player.csv')),
        'df_gameweeks': pd.read_csv(os.path.join(data_dir, 'Gameweeks.csv')),
        'df_player_history': pd.read_csv(os.path.join(data_dir, 'Player_history.csv')),
        'df_players': pd.read_csv(os.path.join(data_dir, 'Players.csv')),
        'df_positions': pd.read_csv(os.path.join(data_dir, 'Positions.csv')),
        'df_teams': pd.read_csv(os.path.join(data_dir, 'Teams.csv')),
        'df_fixtures': pd.read_csv(os.path.join(data_dir, 'Fixtures.csv')),
    }

# Function to prepare the Fixture Difficulty Rating (FDR) table
def prepare_fdr_table(df_fixtures, df_teams):
    # Team mapping
    team_name_mapping = pd.Series(df_teams.team_name.values, index=df_teams.id).to_dict()
    team_short_name_mapping = pd.Series(df_teams.short_name.values, index=df_teams.id).to_dict()
    
    # Replace team IDs with names
    df_fixtures['team_a'] = df_fixtures['team_a'].replace(team_name_mapping)
    df_fixtures['team_h'] = df_fixtures['team_h'].replace(team_name_mapping)

    # Prepare FDR matrix
    upcoming_gameweeks = df_fixtures[df_fixtures['finished'] == False]
    teams = upcoming_gameweeks['team_a'].unique()
    unique_gameweeks = upcoming_gameweeks['event'].unique()
    formatted_gameweeks = [f'GW{gw}' for gw in unique_gameweeks]
    
    fdr_matrix = pd.DataFrame(index=teams, columns=formatted_gameweeks)
    fdr_values = {}
    
    for _, row in upcoming_gameweeks.iterrows():
        gameweek = f'GW{row["event"]}'
        team_a, team_h = row['team_a'], row['team_h']
        fdr_values[(team_a, gameweek)] = row['team_a_difficulty']
        fdr_values[(team_h, gameweek)] = row['team_h_difficulty']
        
        fdr_matrix.at[team_a, gameweek] = f"{team_h} (A)"
        fdr_matrix.at[team_h, gameweek] = f"{team_a} (H)"

    return fdr_matrix.astype(str), fdr_values

# Function to color the FDR based on values
def color_fdr(team, gameweek, fdr_values):
    fdr_value = fdr_values.get((team, gameweek), None)
    
    if fdr_value is None:  # Handle NaN values
        return 'background-color: white;'  # Neutral color for NaN

    # Color coding based on FDR value
    colors = {
        1: '#257d5a',  # Green
        2: '#00ff86',  # Light Green
        3: '#ebebe4',  # Yellow
        4: '#ff005a',  # Orange
        5: '#861d46',  # Red
    }
    return f'background-color: {colors.get(fdr_value, "white")};'

# Function to display fixtures
def display_fixtures(current_gameweek_fixtures):
    for _, match in current_gameweek_fixtures.iterrows():
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

# Main function to run the app
def main():
    # Set up Streamlit app title
    st.title('Fantasy Premier League')

    # Get the absolute path for the data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    data = load_data(data_dir)
    
    # Prepare FDR table
    fdr_matrix, fdr_values = prepare_fdr_table(data['df_fixtures'], data['df_teams'])

    # Add datetime to fixtures for display
    data['df_fixtures']['datetime'] = pd.to_datetime(data['df_fixtures']['kickoff_time'], utc=True)
    data['df_fixtures']['local_hour'] = data['df_fixtures']['datetime'].dt.tz_convert('Europe/London').dt.strftime('%H:%M')

    # Session state for gameweek selection
    if 'selected_gameweek' not in st.session_state:
        st.session_state['selected_gameweek'] = sorted(data['df_fixtures']['event'].unique())[0]

    # Display options
    display_option = st.radio("Select Display", ('Fixture Difficulty Rating', 'Premier League Fixtures'))

    # FDR Display
    if display_option == 'Fixture Difficulty Rating':
        styled_fdr_table = fdr_matrix.style.apply(lambda row: [color_fdr(row.name, col, fdr_values) for col in row.index], axis=1)
        st.write(styled_fdr_table)

    # Premier League Fixtures Display
    elif display_option == 'Premier League Fixtures':
        # Implement dropdown for gameweek selection
        gameweeks = sorted(data['df_fixtures']['event'].unique())
        st.session_state['selected_gameweek'] = st.selectbox("Select Gameweek", gameweeks, index=gameweeks.index(st.session_state['selected_gameweek']))
        
        # Filter fixtures based on selected gameweek
        current_gameweek_fixtures = data['df_fixtures'][data['df_fixtures']['event'] == st.session_state['selected_gameweek']]
        
        # Display fixtures
        st.markdown(f"<h2 style='text-align: center;'>Premier League Fixtures - Gameweek {st.session_state['selected_gameweek']}</h2>", unsafe_allow_html=True)
        display_fixtures(current_gameweek_fixtures)

if __name__ == "__main__":
    main()
