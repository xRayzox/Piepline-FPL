import pandas as pd
from datetime import datetime, timezone
import streamlit as st
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="FPL Fixtures & FDR",
    layout="wide"  # Use the full width of the screen
)

# --- Theme Customization ---
st.markdown(
    """
<style>
    body {
        color: #333;
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    .stMarkdown>h2 {
        text-align: center;
    }
    /* Styles for the FDR table */
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        text-align: center;
        padding: 8px;
        border: 1px solid #ddd; 
    }
    /* Center content */
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh; /* Optional: Center vertically on the page */
    }
    .fixture-container {
        text-align: center;
        margin: 20px;
    }
    .fixture-box {
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        background-color: #f9f9f9; /* Light background for fixture box */
    }
    .fixture-box p {
        margin-bottom: 5px; /* Reduce spacing between team names and score/vs */
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- Data Loading and Preprocessing ---
# Get the absolute path for the data directory
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

# Load DataFrames
df_teams = pd.read_csv(os.path.join(data_dir, "Teams.csv"))
df_fixtures = pd.read_csv(os.path.join(data_dir, "Fixtures.csv"))

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

# --- Streamlit App ---
st.title('Fantasy Premier League: Fixtures & FDR')

# --- Sidebar: Gameweek Navigation and Display Options ---
with st.sidebar:
    st.header("Navigation")

    selected_display = st.radio(
        "Select Display:", ['Premier League Fixtures', 'Fixture Difficulty Rating'] 
    )

# --- Dynamic Gameweek Selection ---
min_gameweek = int(df_fixtures['event'].min())
max_gameweek = int(df_fixtures['event'].max())

# Get the next unfinished gameweek
next_unfinished_gameweek = next(
    (gw for gw in range(min_gameweek, max_gameweek + 1) if df_fixtures[(df_fixtures['event'] == gw) & (df_fixtures['finished'] == False)].shape[0] > 0),
    min_gameweek
)

# --- Premier League Fixtures Display ---
if selected_display == 'Premier League Fixtures':
    # --- Gameweek Navigation ---
    if 'selected_gameweek' not in st.session_state:
        st.session_state.selected_gameweek = next_unfinished_gameweek

    col1, col2, col3 = st.columns([1, 2, 1])  # Adjusted column ratios for better spacing

    with col1:
        if st.button("Previous"):
            st.session_state.selected_gameweek = max(
                st.session_state.selected_gameweek - 1, min_gameweek
            )

    with col3:
        if st.button("Next"):
            st.session_state.selected_gameweek = min(
                st.session_state.selected_gameweek + 1, max_gameweek
            )

    # Selectbox for choosing a specific gameweek (now above the fixtures)
    with col2:
        selected_gameweek = st.selectbox(
            "Select Gameweek:",
            options=range(min_gameweek, max_gameweek + 1),
            index=st.session_state.selected_gameweek - min_gameweek
        )

    st.session_state.selected_gameweek = selected_gameweek

    # --- Display Fixtures for Selected Gameweek ---
    st.markdown(
        f"<h2 style='text-align: center;'>Premier League Fixtures - Gameweek {selected_gameweek}</h2>",
        unsafe_allow_html=True,
    )

    current_gameweek_fixtures = df_fixtures[df_fixtures['event'] == selected_gameweek]
    grouped_fixtures = current_gameweek_fixtures.groupby('local_date')

    # Use centered container for fixtures
    with st.container(): 
        for date, matches in grouped_fixtures:
            st.markdown(f"<h3 style='text-align: center;'>{date}</h3>", unsafe_allow_html=True)
            for _, match in matches.iterrows():
                # Create a fixture box for each match
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 2])

                    with col1:
                        st.markdown(f"**{match['team_h']}**")
                    with col2:
                        if match['finished']:
                            st.markdown(
                                f"<p style='text-align: center; color: green;'>{int(match['team_h_score'])} - {int(match['team_a_score'])}</p>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(f"<p style='text-align: center;'>vs</p>", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"**{match['team_a']}**")

                    if not match['finished']:
                        st.caption(f"Kickoff: {match['local_hour']}")

# --- FDR Matrix Display ---
elif selected_display == 'Fixture Difficulty Rating':
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
    
    # Slider for FDR starting from the upcoming gameweek
    selected_gameweek = st.sidebar.slider(
        "Select Gameweek:",
        min_value=next_unfinished_gameweek,
        max_value=max_gameweek,
        value=next_unfinished_gameweek       
    )

    # --- Filter FDR Table for Next 10 Gameweeks ---
    filtered_fdr_matrix = fdr_matrix.copy()
    filtered_fdr_matrix = filtered_fdr_matrix[[f'GW{gw}' for gw in range(selected_gameweek, selected_gameweek + 10) if f'GW{gw}' in filtered_fdr_matrix.columns]]

    st.markdown(f"**Fixture Difficulty Rating (FDR) for the Next 10 Gameweeks (Starting GW{selected_gameweek})**", unsafe_allow_html=True)
    styled_filtered_fdr_table = filtered_fdr_matrix.style.apply(lambda row: [color_fdr(row.name, col) for col in row.index], axis=1)
    st.write(styled_filtered_fdr_table)

    # --- FDR Legend ---
    with st.sidebar:
        st.markdown("**Legend:**")
        fdr_colors = {
            1: ("#257d5a", "black"),
            2: ("#00ff86", "black"),
            3: ("#ebebe4", "black"),
            4: ("#ff005a", "white"),
            5: ("#861d46", "white"),
        }
        for fdr, (bg_color, font_color) in fdr_colors.items():
            st.sidebar.markdown(
                f"<span style='background-color: {bg_color}; color: {font_color}; padding: 2px 5px; border-radius: 3px;'>"
                f"{fdr} - {'Very Easy' if fdr == 1 else 'Easy' if fdr == 2 else 'Medium' if fdr == 3 else 'Difficult' if fdr == 4 else 'Very Difficult'}"
                f"</span>",
                unsafe_allow_html=True,
            )