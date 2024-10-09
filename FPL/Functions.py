import requests
import pandas as pd
import json

######################################################
# fixture
######################################################
def load_fixture():
    url = 'https://fantasy.premierleague.com/api/fixtures/'  # Correct URL for fixtures
    response = requests.get(url)
    data = json.loads(response.text)
    fixtures_df = pd.DataFrame(data)

    fixtures_df.drop(columns='stats', inplace=True)
    return fixtures_df
######################################################
# FPL static 
######################################################
def load_fpl():
    # Fetch data from the Fantasy Premier League API
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(url)

    # Convert JSON data to Python objects
    data = json.loads(response.text)

    # Create DataFrames for different parts of the data
    players_df = pd.DataFrame(data['elements'])
    teams_df = pd.DataFrame(data['teams'])
    positions_of_players_df = pd.DataFrame(data['element_types'])
    gameweeks_df = pd.DataFrame(data['events'])

    return players_df, teams_df, positions_of_players_df, gameweeks_df

######################################################
# player history
######################################################
base_url = "https://fantasy.premierleague.com/api/element-summary/{player_id}"

def fetch_summary(player_id):
    """
    Function that takes player id and returns their history data.
    """
    response = requests.get(base_url.format(player_id=player_id))
    return response.json()

def load_player_history(df):
    """
    Function to fetch current and previous season data for all players based on their IDs in batches.
    """
    all_players_current = []
    all_players_previous = []
    
    players_ids = df.id.to_list()

    for player_id in players_ids:
        data = fetch_summary(player_id)  # Consider caching this data
        current_season = data.get('history', [])
        previous_seasons = data.get('history_past', [])

        all_players_current.extend(current_season)
        all_players_previous.extend(previous_seasons)

        

    current_season_df = pd.DataFrame(all_players_current)
    previous_seasons_df = pd.DataFrame(all_players_previous)
    return current_season_df, previous_seasons_df