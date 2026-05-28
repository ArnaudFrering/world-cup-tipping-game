from src.generate_games import generate_fixtures_df, load_groups
from src.simulate_match import simulate_match
from src.group_standings import compute_group_standings, standings_between_thirds

import pandas as pd

if __name__ == "__main__":
    groups = load_groups()
    fixtures_df = generate_fixtures_df(groups)

    # simulate one random score (0-3) per team for each fixture
    results_df = fixtures_df.apply(simulate_match, axis=1)
    fixtures_df = pd.concat([fixtures_df, results_df], axis=1)

    # after you have fixtures_df with home_goals/away_goals
    standings_df = compute_group_standings(fixtures_df)
    thirds_ranking = standings_between_thirds(standings_df)
    print(standings_df.head(32))
    print(thirds_ranking.head(12))