import pandas as pd

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

def match_thirds_to_knockout_games(thirds_ranking):
    """
    Match the best 8 thirds from thirds_ranking to knockout games.
    
    Args:
        thirds_ranking: DataFrame with best thirds (should have 'group' column)
    
    Returns:
        DataFrame with 8 knockout games matched to the best thirds
    """
    games_df = preprocess_knockout_games()
    print(games_df.head())
    # Get the best 8 thirds
    best_8_thirds = thirds_ranking.head(8).copy()
    print(best_8_thirds.head())
    # Create a result list to store matched games
    matched_games = []
    
    for idx, game_row in games_df.iterrows():
        game_groups = game_row['groups']
        
        # Find thirds that match this game's groups
        matching_thirds = best_8_thirds[best_8_thirds['group'].isin(game_groups)]
        
        if len(matching_thirds) >= 2:
            matched_games.append({
                'game_id': idx,
                'home_team': matching_thirds.iloc[0]['team'],
                'away_team': matching_thirds.iloc[1]['team'],
                'home_group': matching_thirds.iloc[0]['group'],
                'away_group': matching_thirds.iloc[1]['group'],
                **game_row.to_dict()
            })
    
    return pd.DataFrame(matched_games)