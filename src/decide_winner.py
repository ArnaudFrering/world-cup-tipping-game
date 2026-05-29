import random
from typing import Dict, Any, Optional
import pandas as pd


def decide_winner_elo(home: str, away: str, home_elo: float, away_elo: float, 
                      draw_margin: float = 200, k_factor: float = 32, rng: Optional[random.Random] = None) -> Dict[str, Any]:
    """
    Simulate a match result using a three-outcome ELO model.
    
    Uses the three-outcome ELO formula to calculate probabilities for home win, draw, and away win.
    Then generates scores that match the chosen outcome and calculates updated ELO ratings.
    
    Args:
        home: Home team name
        away: Away team name
        home_elo: Home team ELO rating
        away_elo: Away team ELO rating
        draw_margin: Draw margin parameter (typically 200 for football)
        k_factor: ELO K-factor (default 32, higher for more volatile ratings)
        rng: Random number generator (uses default if None)
    
    Returns:
        Dict with keys: home, away, home_goals, away_goals, result, home_elo_new, away_elo_new
    """
    rnd = rng or random
    
    # Calculate probabilities using three-outcome ELO model
    elo_diff = away_elo - home_elo
    
    # Common denominator for all three probabilities
    denominator = 1 + 10 ** (elo_diff / 400) + 10 ** ((elo_diff - draw_margin) / 400)
    
    # P(home wins) = 1 / denominator
    home_win_prob = 1 / denominator
    
    # P(draw) = 10^((away_elo - home_elo - draw_margin) / 400) / denominator
    draw_prob = 10 ** ((elo_diff - draw_margin) / 400) / denominator
    
    # P(away wins) = 10^((away_elo - home_elo) / 400) / denominator
    away_win_prob = 10 ** (elo_diff / 400) / denominator
    
    # Choose outcome based on probabilities
    outcome = rnd.choices(
        ["home", "away", "draw"],
        weights=[home_win_prob, away_win_prob, draw_prob],
        k=1
    )[0]
    
    # Determine actual score (1 = win, 0.5 = draw, 0 = loss)
    if outcome == "home":
        home_actual_score = 1.0
        away_actual_score = 0.0
    elif outcome == "away":
        home_actual_score = 0.0
        away_actual_score = 1.0
    else:  # draw
        home_actual_score = 0.5
        away_actual_score = 0.5
    
    # Calculate new ELO ratings
    home_elo_new = home_elo + k_factor * (home_actual_score - home_win_prob)
    away_elo_new = away_elo + k_factor * (away_actual_score - away_win_prob)
    
    # Generate scores that match the outcome
    if outcome == "home":
        home_goals = rnd.randint(1, 5)
        away_goals = rnd.randint(0, home_goals - 1)
    elif outcome == "away":
        away_goals = rnd.randint(1, 5)
        home_goals = rnd.randint(0, away_goals - 1)
    else:  # draw
        home_goals = away_goals = rnd.randint(0, 2)
    
    return {
        "home": home,
        "away": away,
        "home_goals": home_goals,
        "away_goals": away_goals,
        "result": outcome,
        "home_elo_new": home_elo_new,
        "away_elo_new": away_elo_new,
    }


def decide_winner(home: str, away: str, max_goals: int = 3, rng: Optional[random.Random] = None) -> Dict[str, Any]:
    """
    Simulate a single match result by choosing random scores between 0 and max_goals (inclusive)
    for both teams.

    Returns a dict with keys:
      - home: home team name
      - away: away team name
      - home_goals: int
      - away_goals: int
      - result: "home", "away" or "draw"
    """
    rnd = rng or random
    home_goals = rnd.randint(0, max_goals)
    away_goals = rnd.randint(0, max_goals)

    if home_goals > away_goals:
        result = "home"
    elif away_goals > home_goals:
        result = "away"
    else:
        result = "draw"

    return {
        "home": home,
        "away": away,
        "home_goals": home_goals,
        "away_goals": away_goals,
        "result": result,
    }


def decide_winner_knockout_phase(row: pd.Series, max_goals: int = 3, rng: Optional[random.Random] = None) -> Dict[str, Any]:
    rnd = rng or random
    home = row['home']
    away = row['away']
    home_goals = rnd.randint(0, max_goals)
    away_goals = rnd.randint(0, max_goals)

    if home_goals >= away_goals:
        result = home
    elif away_goals > home_goals:
        result = away

    return {
        "nb": row['nb'],
        "home": home,
        "away": away,
        "home_goals": home_goals,
        "away_goals": away_goals,
        "result": result,
    }


def decide_winner_knockout_phase_elo(row: pd.Series, team_elos: Dict[str, float], 
                                      draw_margin: float = 200, k_factor: float = 32, 
                                      rng: Optional[random.Random] = None) -> Dict[str, Any]:
    """
    Simulate a knockout match using ELO ratings. No draws allowed - if a draw occurs in probabilities,
    randomly pick a winner while keeping equal goals.
    
    Args:
        row: DataFrame row with 'home', 'away', and 'nb' columns
        team_elos: Dictionary of team ELO ratings (will be modified in-place)
        draw_margin: Draw margin parameter (typically 200 for football)
        k_factor: ELO K-factor (default 32)
        rng: Random number generator (uses default if None)
    
    Returns:
        Dict with keys: nb, home, away, home_goals, away_goals, result, home_elo_new, away_elo_new
    """
    rnd = rng or random
    home = row['home']
    away = row['away']
    home_elo = team_elos[home]
    away_elo = team_elos[away]
    
    # Calculate probabilities using three-outcome ELO model
    elo_diff = away_elo - home_elo
    
    # Common denominator for all three probabilities
    denominator = 1 + 10 ** (elo_diff / 400) + 10 ** ((elo_diff - draw_margin) / 400)
    
    # P(home wins) = 1 / denominator
    home_win_prob = 1 / denominator
    
    # P(draw) = 10^((away_elo - home_elo - draw_margin) / 400) / denominator
    draw_prob = 10 ** ((elo_diff - draw_margin) / 400) / denominator
    
    # P(away wins) = 10^((away_elo - home_elo) / 400) / denominator
    away_win_prob = 10 ** (elo_diff / 400) / denominator
    
    # Choose outcome based on probabilities
    outcome = rnd.choices(
        ["home", "away", "draw"],
        weights=[home_win_prob, away_win_prob, draw_prob],
        k=1
    )[0]
    
    # Track if it was originally a draw
    was_draw = (outcome == "draw")
    
    # If draw, redistribute probabilities and pick a winner
    if outcome == "draw":
        # Renormalize probabilities (remove draw from distribution)
        total_win_prob = home_win_prob + away_win_prob
        home_win_prob_normalized = home_win_prob / total_win_prob
        away_win_prob_normalized = away_win_prob / total_win_prob
        
        # Randomly pick winner based on normalized probabilities
        outcome = rnd.choices(
            ["home", "away"],
            weights=[home_win_prob_normalized, away_win_prob_normalized],
            k=1
        )[0]
    
    # Determine actual score (1 = win, 0 = loss)
    if outcome == "home":
        home_actual_score = 1.0
        away_actual_score = 0.0
    else:  # away
        home_actual_score = 0.0
        away_actual_score = 1.0
    
    # Calculate new ELO ratings
    home_elo_new = home_elo + k_factor * (home_actual_score - home_win_prob)
    away_elo_new = away_elo + k_factor * (away_actual_score - away_win_prob)
    
    # Update team ELOs
    team_elos[home] = home_elo_new
    team_elos[away] = away_elo_new
    
    # Generate scores
    if was_draw:
        # Both teams score the same amount of goals
        home_goals = away_goals = rnd.randint(0, 4)
    else:
        # Different scores based on who won
        if outcome == "home":
            home_goals = rnd.randint(1, 5)
            away_goals = rnd.randint(0, home_goals - 1)
        else:  # away
            away_goals = rnd.randint(1, 5)
            home_goals = rnd.randint(0, away_goals - 1)
    
    # Convert outcome ("home"/"away") to actual team name
    result_team = home if outcome == "home" else away
    
    return {
        "nb": row['nb'],
        "home": home,
        "away": away,
        "home_goals": home_goals,
        "away_goals": away_goals,
        "result": result_team,
        "home_elo_new": home_elo_new,
        "away_elo_new": away_elo_new,
    }