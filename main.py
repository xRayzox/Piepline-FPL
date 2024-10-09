import sys
import pandas as pd
sys.path.append('./FPL')

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

    # You can return the transformed data if needed
    return transformed_players_df, transformed_teams_df, transformed_positions_df, transformed_gameweeks_df

# Define the function to load player statistics
def load_player_statistics():
    # Load players data
    players_df, _, _, _ = load_fpl()
    current_season_df, previous_seasons_df = load_player_history(players_df)
    
    # Transform player history data
    transformed_current_season_df = transform_fact_history(current_season_df)
    transformed_previous_season_df = transform_previous_season(previous_seasons_df)

    # You can return the transformed data if needed
    return transformed_current_season_df, transformed_previous_season_df

def load_fixture_data():
    fixture_df = load_fixture()
    print(fixture_df)

# Main function to execute tasks in sequence
def main():
    transformed_players, transformed_teams, transformed_positions, transformed_gameweeks = load_fpl_data()
    transformed_current_season, transformed_previous_season = load_player_statistics()
    load_fixture_data()

    # You can print or process the transformed data here
    #print(transformed_players)
    print(transformed_teams)

if __name__ == "__main__":
    main()
