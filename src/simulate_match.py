import pandas as pd
from src.decide_winner import decide_winner, decide_winner_elo
import random

rng = random.Random()  # seed if you want reproducible results: Random(42)

def simulate_match(row):
        res = decide_winner(row["home"], row["away"], max_goals=3, rng=rng)
        return pd.Series({
            "home_goals": res["home_goals"],
            "away_goals": res["away_goals"],
            "result": res["result"],
        })

def simulate_match_with_elo(row, team_elos):
    """
    Simulate a match using ELO ratings and update team ELOs.
    
    Args:
        row: DataFrame row with 'home' and 'away' columns
        team_elos: Dictionary of team ELO ratings (will be modified in-place)
    
    Returns:
        pd.Series with match results and updated ELOs
    """
    home = row["home"]
    away = row["away"]
    
    res = decide_winner_elo(
        home, away, 
        team_elos[home], 
        team_elos[away], 
        rng=rng
    )
    
    # Update team ELOs
    team_elos[home] = res["home_elo_new"]
    team_elos[away] = res["away_elo_new"]
    
    return pd.Series({
        "home_goals": res["home_goals"],
        "away_goals": res["away_goals"],
        "result": res["result"],
        "home_elo": res["home_elo_new"],
        "away_elo": res["away_elo_new"],
    })
