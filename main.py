import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), 'FPL'))
from Functions import load_fixture, load_fpl, load_player_history
from Transformation import (transform_fact_history, transform_gameweeks_data, 
                              transform_previous_season, transform_players, 
                              transform_positions, transform_teams)

# Define the function for loading FPL static data
def load_fpl_data():
    players_df, teams_df, positions_of_players_df, gameweeks_df = load_fpl()
    
    # Transform data
    transformed_players_df = transform_players(players_df)
    transformed_teams_df = transform_teams(teams_df)
    transformed_positions_df = transform_positions(positions_of_players_df)
    transformed_gameweeks_df = transform_gameweeks_data(gameweeks_df)

    return transformed_players_df, transformed_teams_df, transformed_positions_df, transformed_gameweeks_df

# Define the function to load player statistics
def load_player_statistics():
    players_df, _, _, _ = load_fpl()
    current_season_df, previous_seasons_df = load_player_history(players_df)
    
    transformed_current_season_df = transform_fact_history(current_season_df)
    transformed_previous_season_df = transform_previous_season(previous_seasons_df)

    return transformed_current_season_df, transformed_previous_season_df

def load_fixture_data():
    fixture_df = load_fixture()
    return fixture_df

# Function to save DataFrame to CSV in the data folder
def save_to_csv(df, file_name):
    # Ensure the 'data' directory exists
    os.makedirs('data', exist_ok=True)
    
    # Save the CSV in the 'data' folder
    file_path = os.path.join('data', file_name)
    df.to_csv(file_path, index=False)
    print(f"Data saved to CSV file: {file_path}")

# Main function to execute tasks in sequence
def main():

    transformed_players, transformed_teams, transformed_positions, transformed_gameweeks = load_fpl_data()
    transformed_current_season, transformed_previous_season = load_player_statistics()
    fixture_df=load_fixture_data()

    # Save the transformed DataFrames as CSV in the 'data' folder
    save_to_csv(transformed_players, 'Players.csv')
    save_to_csv(transformed_teams, 'Teams.csv')
    save_to_csv(transformed_positions, 'Positions.csv')
    save_to_csv(transformed_gameweeks, 'Gameweeks.csv')
    save_to_csv(transformed_current_season, 'Fact_Player.csv')
    save_to_csv(transformed_previous_season, 'Player_history.csv')
    save_to_csv(fixture_df, 'Fixtures.csv')

if __name__ == "__main__":
    main()
