import pandas as pd
from datetime import datetime, timezone
import streamlit as st
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

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

# --- FDR Calculation (Modified for bar chart) ---
fdr_data = df_fixtures[df_fixtures['finished'] == False].copy()

# --- Streamlit App ---
st.title('Fantasy Premier League')

# --- Sidebar: Display Options and Gameweek Selection ---
st.sidebar.header("Navigation and Options")
selected_display = st.sidebar.radio("Select Display:", ['Premier League Fixtures', 'Fixture Difficulty Rating'])

# --- Gameweek Selection (Dynamic based on Display) ---
gameweeks = sorted(df_fixtures['event'].unique())
next_gameweek = next(
    (gw for gw in gameweeks if df_fixtures[(df_fixtures['event'] == gw) & (df_fixtures['finished'] == False)].shape[0] > 0),
    gameweeks[0]
)

if selected_display == 'Premier League Fixtures':
    # Use a Selectbox for Gameweek selection (Fixtures)
    selected_gameweek = st.sidebar.selectbox(
        "Select Gameweek:", 
        gameweeks,
        index=gameweeks.index(next_gameweek) 
    )
else:  # 'Fixture Difficulty Rating'
    # Use a Slider for Gameweek selection (FDR)
    min_gameweek = int(next_gameweek)
    max_gameweek = int(df_fixtures[df_fixtures['finished'] == False]['event'].max())
    selected_gameweek = st.sidebar.slider(
        "Select Gameweek:", 
        min_value=min_gameweek, 
        max_value=max_gameweek, 
        value=min_gameweek 
    )

# --- FDR Bar Chart Visualization ---
if selected_display == 'Fixture Difficulty Rating': 
    st.markdown(f"**Fixture Difficulty Rating (FDR) for the Next 10 Gameweeks (Starting GW{selected_gameweek})**", unsafe_allow_html=True)

    # Filter data for the selected gameweek range
    fdr_data_filtered = fdr_data[fdr_data['event'] >= selected_gameweek].copy()
    fdr_data_filtered['gameweek_label'] = 'GW' + fdr_data_filtered['event'].astype(str)

    # Color mapping for FDR values
    fdr_colors = { 
        1: '#257d5a',  
        2: '#00ff86', 
        3: '#ebebe4', 
        4: '#ff005a', 
        5: '#861d46'   
    }

    # Get unique teams from your filtered DataFrame
    teams = fdr_data_filtered['team_a_short'].unique() 

    # Create the bar charts
    fig, axes = plt.subplots(len(teams), 1, figsize=(10, 2*len(teams)), sharex=True) 
    plt.subplots_adjust(hspace=0.5) 

    for i, team in enumerate(teams):
        team_data = fdr_data_filtered[(fdr_data_filtered['team_a_short'] == team) | (fdr_data_filtered['team_h_short'] == team)]
        team_data = team_data.head(10) # Get only the next 10 gameweeks
        axes[i].bar(team_data['gameweek_label'], team_data['team_h_difficulty'], color=[fdr_colors[fdr] for fdr in team_data['team_h_difficulty']])
        axes[i].set_title(team, fontsize=12)
        axes[i].set_ylim(1, 5) # Set y-axis limits for better visualization
        axes[i].set_yticks([1, 2, 3, 4, 5])  # Set y-axis ticks

    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
    st.pyplot(fig)

    # --- FDR Legend ---
    st.sidebar.markdown("**Legend:**")
    for fdr, color in fdr_colors.items():
        st.sidebar.markdown(
            f"<span style='background-color: {color}; color: {'white' if fdr > 3 else 'black'}; padding: 2px 5px; border-radius: 3px;'>"
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
        st.markdown(f"<div style='text-align: center;'><strong>🕒 {date}</strong></div>", unsafe_allow_html=True)
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