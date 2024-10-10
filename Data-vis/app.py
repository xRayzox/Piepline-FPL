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
filtered_fixtures = df_fixtures[(df_fixtures['finished'] == False) & (df_fixtures['finished_provisional'] == False)]


import pandas as pd

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


