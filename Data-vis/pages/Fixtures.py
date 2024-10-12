import pandas as pd
from datetime import datetime, timezone
import streamlit as st
import os
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

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
    .css-1lcbmhc {
        gap: 5px; /* Adjust this value to reduce the space between columns */
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
        flex-direction: column; /* Stack elements vertically */
        justify-content: center;
        align-items: center;
        text-align: center;
        height: 100vh; /* Optional: Center vertically on the page */
    }
    .fixture-container {
        margin: 10px; /* Reduced margin for compact layout */
        width: 100%; /* Make fixture container take full width */
        text-align: center; /* Center content */
    }
    .fixture-box {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #ddd;
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 5px;
        background-color: #f9f9f9; /* Light background for fixture box */
        text-align: center; /* Center content */
    }
    .fixture-box p {
        margin: 0; /* Remove default paragraph margins for tight spacing */
    }
    .kickoff { /* Style for kickoff time */
        font-size: 0.8rem; /* Slightly smaller font size */
        color: #555; /* Darker gray color */
        text-align: center; /* Center the text */
        margin-top: 5px;
    }
    .score {  /* Style for the score */
        font-weight: bold;
        color: green; /* Green color for the score */
        margin: 0; /* Remove margin */
        text-align: center;
    }
    /* Style the table header (Gameweek labels) */
    .ag-header-cell-label {
        font-weight: bold;
        background-color: #f0f0f0; /* Light gray background */
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
        (gw for gw in range(min_gameweek, max_gameweek + 1) if
         df_fixtures[(df_fixtures['event'] == gw) & (df_fixtures['finished'] == False)].shape[0] > 0),
        min_gameweek
    )

    if selected_display == "Premier League Fixtures":
        if 'selected_gameweek' not in st.session_state:
            st.session_state.selected_gameweek = next_unfinished_gameweek

        selected_gameweek = st.selectbox(
            "Select Gameweek:",
            options=range(min_gameweek, max_gameweek + 1),
            index=st.session_state.selected_gameweek - min_gameweek
        )
        st.session_state.selected_gameweek = selected_gameweek

################# --- Premier League Fixtures Display ---
if selected_display == 'Premier League Fixtures':
    st.markdown(
        f"<h2 style='text-align: center;'>Premier League Fixtures - Gameweek {selected_gameweek}</h2>",
        unsafe_allow_html=True,
    )

    current_gameweek_fixtures = df_fixtures[df_fixtures['event'] == selected_gameweek].copy()
    
    # --- Prepare data for AgGrid ---
    current_gameweek_fixtures['Fixture'] = current_gameweek_fixtures.apply(
        lambda row: f"{row['team_h']} vs {row['team_a']}", axis=1
    )
    current_gameweek_fixtures['Score'] = current_gameweek_fixtures.apply(
        lambda row: f"{int(row['team_h_score'])} - {int(row['team_a_score'])}" if row['finished'] else "-",
        axis=1
    )

    # --- Create AgGrid ---
    gb = GridOptionsBuilder.from_dataframe(current_gameweek_fixtures[['local_date', 'local_hour', 'Fixture', 'Score']])
    gb.configure_column("local_date", header_name="Date", type=["customDateTimeFormat"], custom_format_string='EEE dd MMM yyyy')
    gb.configure_column("local_hour", header_name="Kickoff Time")
    gb.configure_grid_options(domLayout='autoHeight')  # Auto-adjust grid height
    gridOptions = gb.build()

    AgGrid(current_gameweek_fixtures, gridOptions=gridOptions, allow_unsafe_jscode=True)

################# --- FDR Matrix Display ---
elif selected_display == "Fixture Difficulty Rating":
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

    # Slider for FDR starting from the upcoming gameweek
    selected_gameweek = st.sidebar.slider(
        "Select Gameweek:",
        min_value=next_unfinished_gameweek,
        max_value=max_gameweek,
        value=next_unfinished_gameweek
    )

    # --- Filter FDR Table for Next 10 Gameweeks ---
    filtered_fdr_matrix = fdr_matrix.copy()
    filtered_fdr_matrix = filtered_fdr_matrix[
        [f'GW{gw}' for gw in range(selected_gameweek, selected_gameweek + 10) if f'GW{gw}' in
         filtered_fdr_matrix.columns]]

    # --- Create AgGrid for FDR Matrix ---
    fdr_matrix_for_aggrid = filtered_fdr_matrix.reset_index().rename(columns={'index': 'Team'})
    gb = GridOptionsBuilder.from_dataframe(fdr_matrix_for_aggrid)

    # --- Apply cellStyle for color-coding ---
    cellstyle_jscode = JsCode(
        """
        function(params) {
            const fdrValues = {
                '1': {'backgroundColor': '#257d5a', 'color': 'black'},
                '2': {'backgroundColor': '#00ff86', 'color': 'black'},
                '3': {'backgroundColor': '#ebebe4', 'color': 'black'},
                '4': {'backgroundColor': '#ff005a', 'color': 'white'},
                '5': {'backgroundColor': '#861d46', 'color': 'white'}
            };

            const fdr = params.value.match(/\((\d)\)/); // Extract FDR value
            if (fdr && fdrValues[fdr[1]]) {
                return fdrValues[fdr[1]];
            }
        }
        """
    )
    for col in filtered_fdr_matrix.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)

    gb.configure_grid_options(domLayout='autoHeight')
    gridOptions = gb.build()

    st.markdown(
        f"**Fixture Difficulty Rating (FDR) for the Next 10 Gameweeks (Starting GW{selected_gameweek})**",
        unsafe_allow_html=True)

    AgGrid(fdr_matrix_for_aggrid, gridOptions=gridOptions, allow_unsafe_jscode=True)

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