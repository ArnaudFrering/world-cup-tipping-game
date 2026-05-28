import json
import os
import itertools
import pandas as pd
from typing import Dict, List

data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
groups_path = os.path.join(data_dir, "groups.json")

def generate_fixtures_df(groups: Dict[str, List[str]]) -> pd.DataFrame:
    """
    Given a dict of groups -> list of teams, return a DataFrame with one row per match.
    Columns: group, home, away
    """
    rows = []
    for group_name, teams in groups.items():
        for a, b in itertools.combinations(teams, 2):
            rows.append({"group": group_name, "home": a, "away": b})
    return pd.DataFrame(rows)

def load_groups(path: str = groups_path) -> Dict[str, List[str]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)