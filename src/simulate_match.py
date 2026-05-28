import pandas as pd
from src.decide_winner import decide_winner
import random

rng = random.Random()  # seed if you want reproducible results: Random(42)

def simulate_match(row):
        res = decide_winner(row["home"], row["away"], max_goals=3, rng=rng)
        return pd.Series({
            "home_goals": res["home_goals"],
            "away_goals": res["away_goals"],
            "result": res["result"],
        })