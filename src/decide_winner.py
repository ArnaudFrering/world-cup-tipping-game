import random
from typing import Dict, Any, Optional
import pandas as pd

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