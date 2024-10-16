import pandas as pd
import datetime

# Get current date and time
now = datetime.datetime.now()

# Format the date and time as YYYY-MM-DD_HH-MM-SS for safe filename
formatted_datetime = now.strftime("%Y-%m-%d_%H-%M-%S")

def transform_fact_history(input_df):
    # Perform transformations
    input_df['kickoff_time'] = pd.to_datetime(input_df['kickoff_time'])

    float_columns = ['bps', 'influence', 'creativity', 'threat', 'ict_index']
    for col in float_columns:
        input_df[col] = input_df[col].astype(float)

    input_df['value'] = input_df['value'] / 10
    input_df = input_df.rename(columns={
        'round': 'GW',
        'value': 'Cost',
        'minutes': 'minutes_played'
    })

    return input_df  # Return the transformed DataFrame


def transform_gameweeks_data(df):
    # Select needed columns
    needed_columns = ['id', 'name', 'deadline_time', 'highest_score',
                      'average_entry_score', 'most_selected', 'most_transferred_in',
                      'top_element', 'most_captained', 'most_vice_captained',
                      'transfers_made', 'chip_plays']  # Include chip_plays for processing
    
    # Create a copy to avoid SettingWithCopyWarning
    df = df[needed_columns].copy()  

    # Initialize chip columns to zero
    df['bboost'] = 0
    df['3xc'] = 0
    df['wildcard'] = 0
    df['freehit'] = 0

    # Check for chip plays and update counts for each chip type
    for index, row in df.iterrows():
        if isinstance(row['chip_plays'], list) and row['chip_plays']:  # Ensure it's a list and not empty
            for chip in row['chip_plays']:
                chip_name = chip['chip_name']
                if chip_name == 'bboost':
                    df.at[index, 'bboost'] = chip['num_played']
                elif chip_name == '3xc':
                    df.at[index, '3xc'] = chip['num_played']
                elif chip_name == 'wildcard':
                    df.at[index, 'wildcard'] = chip['num_played']
                elif chip_name == 'freehit':
                    df.at[index, 'freehit'] = chip['num_played']

    # Transform 'deadline_time' column
    df['deadline_time'] = pd.to_datetime(df['deadline_time'])
    df = df.rename(columns={'name': 'gw_name'})
    df.drop(columns=['chip_plays'], inplace=True)
    return df


def transform_previous_season(df):
    # Convert costs from integer to float (e.g., 55 to 5.5)
    df['start_cost'] = df['start_cost'] / 10
    df['end_cost'] = df['end_cost'] / 10

    return df  

def transform_players(players_df):
    # Select only the necessary columns

    players_df['now_cost'] = players_df['now_cost'] / 10
    players_df['photo'] = "https://resources.premierleague.com/premierleague/photos/players/250x250/p" + players_df['photo'].str.replace('.jpg', '.png')    
    players_df['news_added'] = pd.to_datetime(players_df['news_added'])
    # Replace empty news entries using .loc
    players_df.loc[players_df['news'] == '', 'news'] = 'No news'
    
    # Create full_name column
    players_df['full_name'] = players_df['first_name'] + ' ' + players_df['second_name']

    # Drop first_name and second_name columns
    players_df = players_df.drop(columns=['first_name', 'second_name'])

    return players_df  # Return the transformed DataFrame for further processing if needed

def transform_positions(positions_df):
    # Select only the necessary columns
    needed_columns = ['id', 'plural_name', 'plural_name_short', 'singular_name', 'singular_name_short','squad_select',
                      'squad_min_play', 'squad_max_play']
    df = positions_df[needed_columns].copy()  # Create a copy to avoid SettingWithCopyWarning

    return df  

def transform_teams(teams_df):
    # Select only the necessary columns
    needed_columns = [
        'code', 'id', 'name', 'short_name', 'strength',
        'strength_overall_away', 'strength_overall_home',
        'strength_attack_away', 'strength_attack_home',
        'strength_defence_away', 'strength_defence_home'
    ]
    
    df = teams_df[needed_columns].copy()  # Create a copy to avoid SettingWithCopyWarning

    # Rename the 'name' column to 'team_name' using .loc
    df.rename(columns={'name': 'team_name'}, inplace=True)

    return df  # Return the transformed DataFrame for further processing if needed
