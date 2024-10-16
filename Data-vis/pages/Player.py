import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import os

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

# Load all CSV files
df_teams = pd.read_csv(os.path.join(data_dir, "Teams.csv"))
df_fixtures = pd.read_csv(os.path.join(data_dir, "Fixtures.csv"))
df_fact_player = pd.read_csv(os.path.join(data_dir, "Fact_Player.csv"))
df_gameweeks = pd.read_csv(os.path.join(data_dir, "Gameweeks.csv"))
df_player_history = pd.read_csv(os.path.join(data_dir, "Player_history.csv"))
df_players = pd.read_csv(os.path.join(data_dir, "Players.csv"))
df_positions = pd.read_csv(os.path.join(data_dir, "Positions.csv"))


# Create a mapping from code in df_teams to team_code
code_mapping = df_teams.set_index('code').to_dict()['team_name']  # Adjust as needed
position_mapping = df_positions.set_index('id').to_dict()['singular_name_short']  # Assuming you want position_name

# Replace element_type in df_player
df_players['element_type'] = df_players['element_type'].map(position_mapping)
df_players['team_code'] = df_players['team_code'].map(code_mapping)


# Streamlit page title
st.title("Fantasy Premier League Player Performance Analysis")

# Sidebar for user input
st.sidebar.header("Filter Options")

# Player position selection
positions = df_players['element_type'].unique()
selected_position = st.sidebar.selectbox("Select Position", positions)

# Filter the DataFrame based on the selected position
filtered_players = df_players[df_players['element_type'] == selected_position]

# Player selection for comparison
selected_players = st.sidebar.multiselect(
    "Select Players for Comparison",
    options=filtered_players['web_name'].unique(),
    default=filtered_players['web_name'].unique()[:5]  # Default to first 5 players
)

# Points per Cost Calculation
filtered_players['pp_cost'] = filtered_players['total_points'] / filtered_players['now_cost']

# Top 10 Value Players
top_value_players = filtered_players.nlargest(10, 'pp_cost')

# Plotting Top Value Players
st.subheader("Top Value Players (Points per Cost)")
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=top_value_players, x='web_name', y='pp_cost', ax=ax)
plt.xticks(rotation=45)
plt.ylabel('Points per Cost')
plt.title('Top 10 Value Players')
st.pyplot(fig)

# Scatter Plot for Selected Players
if selected_players:
    selected_data = filtered_players[filtered_players['web_name'].isin(selected_players)]
    
    st.subheader("Cost vs Total Points for Selected Players")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=selected_data, x='now_cost', y='total_points', hue='web_name', s=100, ax=ax)
    plt.xlabel('Cost')
    plt.ylabel('Total Points')
    plt.title('Cost vs Total Points for Selected Players')
    st.pyplot(fig)

    # Radar Chart for Selected Players
    st.subheader("Performance Metrics for Selected Players")
    radar_data = selected_data[['web_name', 'goals_scored', 'assists', 'clean_sheets', 'points_per_game']]
    
    # Create a radar chart
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    num_vars = len(radar_data.columns) - 1
    angles = [n / float(num_vars) * 2 * 3.141592653589793 for n in range(num_vars)]
    angles += angles[:1]

    for index, row in radar_data.iterrows():
        values = row[1:].values.flatten().tolist()
        values += values[:1]
        ax.fill(angles, values, alpha=0.1)
        ax.plot(angles, values, label=row['web_name'])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(radar_data.columns[1:])
    ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
    plt.title('Performance Metrics Radar Chart')
    st.pyplot(fig)

# Add your contact or other information
st.sidebar.markdown("---")
st.sidebar.write("Created by Your Name")