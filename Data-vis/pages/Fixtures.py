import pandas as pd
from datetime import datetime, timezone
import streamlit as st
import os

# Get the absolute path for the data directory
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

# Load DataFrames 
df_teams = pd.read_csv(os.path.join(data_dir, 'Teams.csv'))
df_fixtures = pd.read_csv(os.path.join(data_dir, 'Fixtures.csv'))

# --- Data Preprocessing (Including Fixtures) ---
team_name_mapping = pd.Series(df_teams.team_name.values, index=df_teams.id).to_dict()
team_short_name_mapping = pd.Series(df_teams.short_name.values, index=df_teams.id).to_dict()
df_fixtures['team_a'] = df_fixtures['team_a'].replace(team_name_mapping)
df_fixtures['team_h'] = df_fixtures['team_h'].replace(team_name_mapping)
df_fixtures['team_a_short'] = df_fixtures['team_a'].map(lambda x: team_short_name_mapping[df_teams[df_teams.team_name == x].id.values[0]] if x in team_name_mapping.values() else None)
df_fixtures['team_h_short'] = df_fixtures['team_h'].map(lambda x: team_short_name_mapping[df_teams[df_teams.team_name == x].id.values[0]] if x in team_name_mapping.values() else None)
df_fixtures = df_fixtures.drop(columns=['pulse_id'])

# Add datetime columns
df_fixtures['datetime'] = pd.to_datetime(df_fixtures['kickoff_time'], utc=True)
df_fixtures['local_time'] = df_fixtures['datetime'].dt.tz_convert('Europe/London').dt.strftime('%A %d %B %Y %H:%M')
df_fixtures['local_date'] = df_fixtures['datetime'].dt.tz_convert('Europe/London').dt.strftime('%A %d %B %Y')
df_fixtures['local_hour'] = df_fixtures['datetime'].dt.tz_convert('Europe/London').dt.strftime('%H:%M')

# --- FDR Matrix Calculation ---
upcoming_gameweeks = df_fixtures[df_fixtures['finished'] == False]
teams = upcoming_gameweeks['team_a_short'].unique()
unique_gameweeks = upcoming_gameweeks['event'].unique()
formatted_gameweeks = [f'GW{gw}' for gw in unique_gameweeks]
fdr_matrix = pd.DataFrame(index=teams, columns=formatted_gameweeks)
fdr_values = {}

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

# --- Color Coding Function ---
def color_fdr(team, gameweek):
    fdr_value = fdr_values.get((team, gameweek), None)
    colors = {
        1: ('#257d5a', 'black'), 
        2: ('#00ff86', 'black'),  
        3: ('#ebebe4', 'black'), 
        4: ('#ff005a', 'white'),  
        5: ('#861d46', 'white'),   
    }
    bg_color, font_color = colors.get(fdr_value, ('white', 'black'))
    return f'background-color: {bg_color}; color: {font_color};'

# --- Streamlit App ---
st.title('Fantasy Premier League')

# --- Sidebar: Gameweek Navigation and Display Options ---
st.sidebar.header("Navigation and Options")

# Display Option
selected_display = st.sidebar.radio(
    "Select Display:", 
    ['Premier League Fixtures', 'Fixture Difficulty Rating'] 
)

# --- Dynamic Gameweek Selection based on Display Option ---
min_gameweek = int(df_fixtures['event'].min())
max_gameweek = int(df_fixtures['event'].max())

# Get the next unfinished gameweek 
next_unfinished_gameweek = next(
    (gw for gw in range(min_gameweek, max_gameweek + 1) if df_fixtures[(df_fixtures['event'] == gw) & (df_fixtures['finished'] == False)].shape[0] > 0),
    min_gameweek  # Default to the first gameweek if all games are finished
)

if selected_display == 'Fixture Difficulty Rating':
    # Slider for FDR starting from the upcoming gameweek
    selected_gameweek = st.sidebar.slider(
        "Select Gameweek:",
        min_value=next_unfinished_gameweek,
        max_value=max_gameweek,
        value=next_unfinished_gameweek       
    )
else:
    # Selectbox for Premier League Fixtures defaulting to upcoming gameweek
    selected_gameweek = st.sidebar.selectbox(
        "Select Gameweek:",
        options=range(min_gameweek, max_gameweek + 1),
        index=next_unfinished_gameweek - min_gameweek  # Default to upcoming gameweek
    )

# --- FDR Matrix Calculation and Display ---
if selected_display == 'Fixture Difficulty Rating': 
    # --- Filter FDR Table for Next 10 Gameweeks ---
    filtered_fdr_matrix = fdr_matrix.copy()
    filtered_fdr_matrix = filtered_fdr_matrix[[f'GW{gw}' for gw in range(selected_gameweek, selected_gameweek + 10) if f'GW{gw}' in filtered_fdr_matrix.columns]]

    st.markdown(f"**Fixture Difficulty Rating (FDR) for the Next 10 Gameweeks (Starting GW{selected_gameweek})**", unsafe_allow_html=True)
    styled_filtered_fdr_table = filtered_fdr_matrix.style.apply(lambda row: [color_fdr(row.name, col) for col in row.index], axis=1)
    st.write(styled_filtered_fdr_table)

    # --- FDR Legend ---
    st.sidebar.markdown("**Legend:**")
    fdr_colors = { 
        1: ('#257d5a', 'black'),  
        2: ('#00ff86', 'black'), 
        3: ('#ebebe4', 'black'), 
        4: ('#ff005a', 'white'), 
        5: ('#861d46', 'white')   
    }
    for fdr, (bg_color, font_color) in fdr_colors.items():
        st.sidebar.markdown(
            f"<span style='background-color: {bg_color}; color: {font_color}; padding: 2px 5px; border-radius: 3px;'>"
            f"{fdr} - {'Very Easy' if fdr == 1 else 'Easy' if fdr == 2 else 'Medium' if fdr == 3 else 'Difficult' if fdr == 4 else 'Very Difficult'}"
            f"</span>",
            unsafe_allow_html=True
        )

# --- Premier League Fixtures Display ---
elif selected_display == 'Premier League Fixtures':
    st.markdown(f"<h2 style='text-align: center;'>Premier League Fixtures - Gameweek {selected_gameweek}</h2>", unsafe_allow_html=True)
    current_gameweek_fixtures = df_fixtures[df_fixtures['event'] == selected_gameweek]
    grouped_fixtures = current_gameweek_fixtures.groupby('local_date')

    for date, matches in grouped_fixtures:
        st.markdown(f"<div style='text-align: center;'><strong> {date}</strong></div>", unsafe_allow_html=True)
        for _, match in matches.iterrows():
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