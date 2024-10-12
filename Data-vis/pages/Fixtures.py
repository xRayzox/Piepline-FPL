import pandas as pd
import streamlit as st
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="FPL Fixtures & FDR",
    layout="wide"
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
        gap: 5px;
    }
    .stMarkdown>h2 {
        text-align: center;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        text-align: center;
        padding: 8px;
        border: 1px solid #ddd; 
    }
    .centered {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        height: 100vh;
    }
    .fixture-container {
        margin: 10px;
        width: 100%;
        text-align: center; 
    }
    .fixture-box {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #ddd;
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 5px;
        background-color: #f9f9f9;
        text-align: center; 
    }
    .fixture-box p {
        margin: 0;
    }
    .kickoff { 
        font-size: 0.8rem; 
        color: #555; 
        text-align: center; 
        margin-top: 5px;
    }
    .score { 
        font-weight: bold;
        color: green; 
        margin: 0; 
        text-align: center;
    }
    /* Style for Attack and Defense Stars */
    .star-rating {
        font-size: 1.5rem; 
        color: gold;
    }
    .star-rating::before {
        content: '☆☆☆☆☆';
    }
    .star-rating[data-rating="1"]::before {
        content: '★☆☆☆☆';
    }
    .star-rating[data-rating="2"]::before {
        content: '★★☆☆☆';
    }
    .star-rating[data-rating="3"]::before {
        content: '★★★☆☆';
    }
    .star-rating[data-rating="4"]::before {
        content: '★★★★☆';
    }
    .star-rating[data-rating="5"]::before {
        content: '★★★★★';
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

# --- Data Preprocessing ---
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

# --- Get Unique Gameweeks ---
gameweeks = [f'GW{gw}' for gw in sorted(df_fixtures['event'].unique())]

# --- Streamlit App ---
st.title('Fantasy Premier League: Team Strength & FDR')

# --- Sidebar: Gameweek Selection ---
with st.sidebar:
    st.header("Navigation")
    selected_gameweek_index = st.selectbox(
        "Select Gameweek:", 
        gameweeks,
        index=0  # Start with the first gameweek in the list
    )

# Get the selected gameweek as an integer (e.g., 8 from 'GW8')
selected_gameweek_num = int(selected_gameweek_index.replace("GW", ""))

# --- Extract Attack, Defense, and Points Data from Your DataFrames ---
team_data = {}
for index, row in df_teams.iterrows():
    team_name = row['team_name']
    team_data[team_name] = {
        'Att': row['strength_attack_home'],
        'Def': row['strength_defence_home'],
        'Pts': 0 
    }

# --- Calculate Points (You'll need to implement your points logic here) ---
# Example: Award 3 points for a win, 1 for a draw
for index, row in df_fixtures.iterrows():
    if row['finished'] and row['event'] <= selected_gameweek_num:  # Consider only finished games up to the selected gameweek
        if row['team_h_score'] > row['team_a_score']:
            team_data[row['team_h']]['Pts'] += 3
        elif row['team_h_score'] == row['team_a_score']:
            team_data[row['team_h']]['Pts'] += 1
            team_data[row['team_a']]['Pts'] += 1
        else:
            team_data[row['team_a']]['Pts'] += 3

# --- Prepare Data for FDR Matrix ---
fdr_data = {}
for index, row in df_fixtures.iterrows():
    gameweek = f'GW{row["event"]}'
    team_a = row['team_a_short']
    team_h = row['team_h_short']
    fdr_a = row['team_a_difficulty']
    fdr_h = row['team_h_difficulty']

    if team_a not in fdr_data:
        fdr_data[team_a] = {}
    fdr_data[team_a][gameweek] = f"{team_h} ({fdr_a:.2f})"

    if team_h not in fdr_data:
        fdr_data[team_h] = {} 
    fdr_data[team_h][gameweek] = f"{team_a} ({fdr_h:.2f})" 

# --- Display Team Strength ---
st.subheader("Team Strength")
st.markdown("This table shows the attack and defense strength of each team based on a 5-star rating system.")

# Convert team_data dictionary to a DataFrame for better display
team_data_df = pd.DataFrame.from_dict(team_data, orient='index').reset_index()
team_data_df.columns = ['Team', 'Att', 'Def', 'Pts']

for index, row in team_data_df.iterrows():
    col1, col2, col3, col4 = st.columns([2, 2, 1, 5])  
    with col1:
        st.write(row['Team'])
    with col2:
        st.markdown(f"<div class='star-rating' data-rating='{int(row['Att'])}'></div>", unsafe_allow_html=True) 
    with col3:
        st.markdown(f"<div class='star-rating' data-rating='{int(row['Def'])}'></div>", unsafe_allow_html=True) 
    with col4:
        st.write(f"**Pts:** {row['Pts']:.1f}")

# --- Display FDR Matrix ---
st.subheader("Fixture Difficulty Rating (FDR)")
st.markdown(f"This table shows the FDR for each team in **{selected_gameweek_index}**.  Lower numbers indicate easier fixtures.")

fdr_df = pd.DataFrame(fdr_data).T
fdr_df = fdr_df[[col for col in gameweeks if col in fdr_df.columns]] # Order columns by gameweek 
st.table(fdr_df[selected_gameweek_index]) 

# --- FDR Legend ---
st.sidebar.markdown("**FDR Legend:**")
fdr_colors = {
    (1.0, 1.5): ("#257d5a", "black", "Very Easy"),  # Dark Green
    (1.51, 2.0): ("#00ff86", "black", "Easy"),      # Light Green
    (2.01, 2.5): ("#ebebe4", "black", "Medium"),    # Light Gray
    (2.51, 3.0): ("#ff005a", "white", "Difficult"),   # Red
    (3.01, 5.0): ("#861d46", "white", "Very Difficult") # Dark Red 
}
for (fdr_min, fdr_max), (bg_color, font_color, label) in fdr_colors.items():
    st.sidebar.markdown(
        f"<span style='background-color: {bg_color}; color: {font_color}; padding: 2px 5px; border-radius: 3px;'>"
        f"{fdr_min:.2f} - {fdr_max:.2f} - {label}"
        f"</span>",
        unsafe_allow_html=True,
    )