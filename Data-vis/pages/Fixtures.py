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

# --- Data Loading (Example Data) ---
data = {
    'Team': ['Liverpool', 'Arsenal', 'Man City', 'Newcastle', 'Chelsea', 'Spurs', 
             'Aston Villa', 'Man Utd', 'Crystal Palace', 'Fulham', 'Bournemouth'],
    'Att': [5, 4, 5, 4, 4, 4, 3, 5, 4, 3, 3],
    'Def': [4, 5, 4, 3, 3, 4, 3, 4, 3, 3, 3],
    'Pts': [7.7, 7, 7.7, 7.5, 7, 8.4, 7, 9.2, 7.9, 8.2, 7.2],
    'GW8': [['CHE (H)', 1.44], ['BOU (A)', 1.12], ['WOL (A)', 1.27], ['BHA (H)', 1.73],
            ['LIV (A)', 0.78], ['WHU (H)', 1.68], ['FUL (A)', 1.10], ['BRE (H)', 1.54],
            ['NFO (A)', 1.14], ['AVL (H)', 1.50], ['ARS (H)', 1.00]],
    'GW9': [['ARS (A)', 0.60], ['LIV (H)', 1.24], ['SOU (H)', 1.84], ['CHE (A)', 0.95],
            ['NEW (H)', 1.39], ['CRY (A)', 1.04], ['BOU (H)', 1.52], ['WHU (A)', 1.18],
            ['TOT (H)', 1.52], ['EVE (A)', 1.24], ['AVL (A)', 1.01]],
    # Add data for more gameweeks (GW10 to GW13) in a similar format
    'GW10': [['BHA (H)', 1.73], ['NEW (A)', 0.90], ['BOU (A)', 1.12], ['ARS (H)', 1.00],
             ['MUN (A)', 1.05], ['AVL (H)', 1.50], ['TOT (A)', 1.02], ['CHE (A)', 1.44],
             ['WOL (A)', 1.27], ['BRE (H)', 1.54], ['MCI (H)', 1.09]],
    'GW11': [['AVL (H)', 1.50], ['CHE (A)', 0.95], ['BHA (A)', 1.23], ['NFO (A)', 1.14],
             ['ARS (H)', 1.00], ['IPS (H)', 1.83], ['LIV (A)', 0.78], ['LEI (H)', 1.79],
             ['FUL (H)', 1.50], ['CRY (A)', 1.04], ['BHA (H)', 1.73]],
    'GW12': [['SOU (A)', 1.34], ['NFO (H)', 1.54], ['TOT (H)', 1.52], ['WHU (H)', 1.58],
             ['LEI (A)', 1.23], ['MCI (A)', 0.66], ['CRY (H)', 1.54], ['IPS (A)', 1.39],
             ['AVL (A)', 1.01], ['WOL (H)', 1.77], ['WOL (A)', 1.27]]
    # ... add more gameweeks as needed
}
df = pd.DataFrame(data)

# --- Preprocess Data ---
gameweeks = [col for col in df.columns if col.startswith('GW')]

# --- Streamlit App ---
st.title('Fantasy Premier League: Team Strength & FDR')

# --- Sidebar: Gameweek Selection ---
with st.sidebar:
    st.header("Navigation")
    selected_gameweek = st.selectbox(
        "Select Gameweek:", 
        gameweeks,
        index=0  # Start with the first gameweek in the list
    )

# --- Display Team Strength ---
st.subheader("Team Strength")
st.markdown("This table shows the attack and defense strength of each team based on a 5-star rating system.")

for index, row in df.iterrows():
    col1, col2, col3, col4 = st.columns([2, 2, 1, 5])  
    with col1:
        st.write(row['Team'])
    with col2:
        st.markdown(f"<div class='star-rating' data-rating='{row['Att']}'></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='star-rating' data-rating='{row['Def']}'></div>", unsafe_allow_html=True)
    with col4:
        st.write(f"**Pts:** {row['Pts']:.1f}")

# --- Display FDR Matrix ---
st.subheader("Fixture Difficulty Rating (FDR)")
st.markdown(f"This table shows the FDR for each team in **{selected_gameweek}**.  Lower numbers indicate easier fixtures.")

# Select and display data for the selected gameweek
selected_gw_data = df[['Team', selected_gameweek]].copy()
selected_gw_data[selected_gameweek] = selected_gw_data[selected_gameweek].apply(lambda x: x if isinstance(x, str) else f"{x[0]} ({x[1]:.2f})")
st.table(selected_gw_data.set_index('Team')) 

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