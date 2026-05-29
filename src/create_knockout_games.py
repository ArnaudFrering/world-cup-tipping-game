import pandas as pd
from typing import Dict, List, Optional, Tuple
import random

HARDCODED_GAMES_ROUND_OF_32 = {
    "73": ["2A", "2B"],
    "76": ["1C", "2F"],
    "75": ["1F", "2C"],
    "78": ["2E", "2I"],
    "84": ["1H", "2J"],
    "83": ["2K", "2L"],
    "88": ["2D", "2G"],
    "86": ["1J", "2H"]
}

def preprocess_knockout_games():
    """
    Load and preprocess the knockout games CSV.
    Creates a column with the list of groups that feed into each game.
    """
    games_df = pd.read_csv('data/table_game_best_3rds.csv')
    
    # Create a column with non-empty columns (A through L)
    group_columns = [col for col in 'ABCDEFGHIJKL' if col in games_df.columns]
    
    # Extract non-empty values for each row
    games_df['groups'] = games_df[group_columns].apply(
        lambda row: [val for val in row if pd.notna(val) and val != ''],
        axis=1
    )
    
    return games_df

def match_thirds_to_knockout_games(group_list_of_3rds):
    """
    Match the best 8 thirds from thirds_ranking to knockout games.
    
    Args:
        thirds_ranking: DataFrame with best thirds (should have 'group' column)
    
    Returns:
        DataFrame with 8 knockout games matched to the best thirds
    """

    mapping_keys = [
        ("79", "1A"),
        ("85", "1B"),
        ("81", "1D"),
        ("74", "1E"),
        ("82", "1G"),
        ("77", "1I"),
        ("87", "1K"),
        ("80", "1L"),
    ]

    games_df = preprocess_knockout_games()
    filtered_games = games_df[
        games_df["groups"].apply(lambda g: sorted(g) == sorted(group_list_of_3rds))
    ]
    row = filtered_games.iloc[0]
    result = {k: [col, row[col]] for k, col in mapping_keys}
    result.update(HARDCODED_GAMES_ROUND_OF_32)
    return result

def create_round_of_32(standings_df, group_list_of_3rds):
    result = match_thirds_to_knockout_games(group_list_of_3rds)
    rows = []
    for nb, placements in result.items():
        home_placement, away_placement = placements
        rows.append({
            'nb': nb,
            'home_placement': home_placement,
            'away_placement': away_placement
        })

    # Step 2: Create a DataFrame from the rows
    matches_df = pd.DataFrame(rows)

    # Step 3: Map placements to team names using standings_df
    # Create a dictionary for quick lookup: {group_and_position: team}
    placement_to_team = dict(zip(standings_df['group_and_position'], standings_df['team']))

    # Map home_placement and away_placement to team names
    matches_df['home'] = matches_df['home_placement'].map(placement_to_team)
    matches_df['away'] = matches_df['away_placement'].map(placement_to_team)

    # Step 4: Reorder columns
    matches_df = matches_df[['nb', 'home_placement', 'away_placement', 'home', 'away']]

    # Display the result
    return matches_df

def generate_next_round(
        results_df: pd.DataFrame,
        hardcoded_games: Dict[str, List[str]]
    ) -> pd.DataFrame:
    """
    Generate the next round's matchups based on the winners of the previous round.

    Args:
        results_df: DataFrame with columns 'nb', 'home', 'away', 'result', etc.
        hardcoded_games: Dictionary where keys are new game numbers and values are lists of previous game numbers.

    Returns:
        DataFrame with columns 'nb', 'home', 'away' for the next round.
    """
    next_round_rows = []

    for new_nb, prev_games in hardcoded_games.items():
        home_game = prev_games[0]
        away_game = prev_games[1]

        # Convert to int for comparison (handle both string and int nb values)
        try:
            home_game_int = int(home_game)
            away_game_int = int(away_game)
        except (ValueError, TypeError):
            home_game_int = home_game
            away_game_int = away_game

        # Get the result of the home_game
        home_game_result = results_df[results_df['nb'] == home_game_int]
        if home_game_result.empty:
            home_game_result = results_df[results_df['nb'] == home_game]
        
        if home_game_result.empty:
            raise ValueError(f"Game {home_game}/{home_game_int} not found in results_df")
        
        home_team = home_game_result.iloc[0]['result']

        # Get the result of the away_game
        away_game_result = results_df[results_df['nb'] == away_game_int]
        if away_game_result.empty:
            away_game_result = results_df[results_df['nb'] == away_game]
        
        if away_game_result.empty:
            raise ValueError(f"Game {away_game}/{away_game_int} not found in results_df")
        
        away_team = away_game_result.iloc[0]['result']

        # Add to the next round
        next_round_rows.append({
            'nb': new_nb,
            'home': home_team,
            'away': away_team
        })

    # Create the new DataFrame
    next_round_df = pd.DataFrame(next_round_rows)
    return next_round_df

def generate_final_and_third_place(
        semifinal_results_df: pd.DataFrame,
    ) -> pd.DataFrame:
    # Extract the semifinal games
    semifinal_1 = semifinal_results_df[semifinal_results_df['nb'] == "101"].iloc[0]
    semifinal_2 = semifinal_results_df[semifinal_results_df['nb'] == "102"].iloc[0]

    # Determine winners and losers (assuming 'result' column contains the winning team name)
    winner_1 = semifinal_1['result']
    loser_1 = semifinal_1['home'] if winner_1 == semifinal_1['away'] else semifinal_1['away']

    winner_2 = semifinal_2['result']
    loser_2 = semifinal_2['home'] if winner_2 == semifinal_2['away'] else semifinal_2['away']

    # Create the final and third-place matchups
    final_and_third_place_rows = [
        {'nb': "103", 'home': loser_1, 'away': loser_2},   # Third-place match
        {'nb': "104", 'home': winner_1, 'away': winner_2},  # Final
    ]

    return pd.DataFrame(final_and_third_place_rows)