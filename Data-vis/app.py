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
filtered_fixtures = df_fixtures[(df_fixtures['finished'] == False) & (df_fixtures['finished_provisional'] == False)]

# Step 1: Prepare the Data
upcoming_gameweeks = df_fixtures[df_fixtures['finished'] == False]

# Initialize a list to hold the FDR records
fdr_records = []

# Iterate over each fixture to assign FDR
for index, row in upcoming_gameweeks.iterrows():
    team_a = row['team_a']
    team_a_short = row['team_a_short']  # Get the short name for team_a
    team_h = row['team_h']
    team_h_short = row['team_h_short']  # Get the short name for team_h
    
    # Create a record for team_a
    fdr_records.append({
        'Team': team_a_short,  # Use the short name for display
        'Gameweek': row['event'],
        'FDR': row['team_a_difficulty'],
        'tooltip': f"{team_a_short} - FDR {row['team_a_difficulty']}"  # Add tooltip for team_a
    })

    # Create a record for team_h
    fdr_records.append({
        'Team': team_h_short,  # Use the short name for display
        'Gameweek': row['event'],
        'FDR': row['team_h_difficulty'],
        'tooltip': f"{team_h_short} - FDR {row['team_h_difficulty']}"  # Add tooltip for team_h
    })

# Step 2: Create a DataFrame from the records
fdr_results = pd.DataFrame(fdr_records)

# Step 3: Pivot the DataFrame to create the FDR table
fdr_table = fdr_results.pivot(index='Team', columns='Gameweek', values='FDR')

# Create a corresponding pivot table for tooltips
tooltip_table = fdr_results.pivot(index='Team', columns='Gameweek', values='tooltip')

# Step 4: Define a function to format the DataFrame with team name and tooltip
def format_fdr_with_tooltip(val, tooltip):
    if pd.isna(val):  # Handle NaN values
        return '', ''  # No display for NaN
    else:
        return f"{val}", tooltip  # Display value with tooltip

# Step 5: Create a function to apply styling with tooltips
def apply_tooltip(fdr_df, tooltip_df):
    formatted_table = fdr_df.copy()

    for col in fdr_df.columns:
        formatted_table[col] = fdr_df[col].apply(lambda x: f'<span title="{tooltip_df[col][x]}">{x}</span>' if not pd.isna(x) else '')

    return formatted_table

# Step 6: Apply the tooltips to the FDR table
styled_fdr_table = apply_tooltip(fdr_table, tooltip_table)

# Step 7: Define a function to color the DataFrame based on FDR values
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

# Step 8: Apply the color function to the DataFrame using applymap
styled_fdr_table = fdr_table.style.applymap(color_fdr)

# Title of the app
st.title('Fantasy Premier League Fixture Difficulty Ratings')

# Display the styled table with tooltips
st.write(styled_fdr_table)
