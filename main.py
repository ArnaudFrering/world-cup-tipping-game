from src.generate_games import generate_fixtures_df, load_groups
from src.simulate_match import simulate_match, simulate_match_with_elo
from src.group_standings import compute_group_standings, standings_between_thirds
from src.create_knockout_games import create_round_of_32, generate_next_round, generate_final_and_third_place
from src.decide_winner import decide_winner_knockout_phase_elo
from src.calculate_points import calculate_points, sum_points_by_team, sum_knockout_points_by_team, combine_total_points
from src.analysis import extract_final_elos

import pandas as pd
import json
import random

with open('data/first_elo scores.json') as f:
    team_elos = json.load(f)

rng = random.Random()  # seed if you want reproducible results: Random(42)

HARDCODED_GAMES_ROUND_OF_16 = {
    "90": ["73", "75"],
    "89": ["74", "77"],
    "91": ["76", "78"],
    "92": ["79", "80"],
    "93": ["83", "84"],
    "94": ["81", "82"],
    "95": ["86", "88"],
    "96": ["85", "87"]
}

HARDCODED_GAMES_QUARTERFINALS = {
    "97": ["89", "90"],
    "98": ["93", "94"],
    "99": ["91", "92"],
    "100": ["95", "96"],
}

HARDCODED_GAMES_SEMIFINALS = {
    "101": ["97", "98"],
    "102": ["99", "100"],
}

HARDCODED_GAMES_FINALS = {
    "103": ["101", "102"], #match for the third place
    "104": ["101", "102"],
}

if __name__ == "__main__":
    groups = load_groups()
    fixtures_df = generate_fixtures_df(groups)
    # simulate matches using ELO ratings and track ELO evolution
    results_df = fixtures_df.apply(lambda row: simulate_match_with_elo(row, team_elos), axis=1)
    fixtures_df = pd.concat([fixtures_df, results_df], axis=1)
    # after you have fixtures_df with home_goals/away_goals
    standings_df = compute_group_standings(fixtures_df)
    thirds_ranking = standings_between_thirds(standings_df)
    group_list_of_3rds = sorted(thirds_ranking["group_letter"].unique())
    
    # Match best 8 thirds to knockout games
    knockout_games = create_round_of_32(standings_df, group_list_of_3rds)
    results_knockout_games_df = knockout_games.apply(
        lambda row: decide_winner_knockout_phase_elo(row, team_elos, rng=rng), axis=1
    )
    results_knockout_games_df = pd.DataFrame(results_knockout_games_df.tolist())

    knockout_games_round_of_16 = generate_next_round(results_knockout_games_df, HARDCODED_GAMES_ROUND_OF_16)
    results_knockout_games_round_of_16 = knockout_games_round_of_16.apply(
        lambda row: decide_winner_knockout_phase_elo(row, team_elos, rng=rng), axis=1
    )
    results_knockout_games_round_of_16 = pd.DataFrame(results_knockout_games_round_of_16.tolist())

    quarterfinals = generate_next_round(results_knockout_games_round_of_16, HARDCODED_GAMES_QUARTERFINALS)
    results_quarterfinals = quarterfinals.apply(
        lambda row: decide_winner_knockout_phase_elo(row, team_elos, rng=rng), axis=1
    )
    results_quarterfinals = pd.DataFrame(results_quarterfinals.tolist())

    semifinals = generate_next_round(results_quarterfinals, HARDCODED_GAMES_SEMIFINALS)
    results_semifinals = semifinals.apply(
        lambda row: decide_winner_knockout_phase_elo(row, team_elos, rng=rng), axis=1
    )
    results_semifinals = pd.DataFrame(results_semifinals.tolist())

    final_and_third_place_df  = generate_final_and_third_place(results_semifinals)
    results_final_and_third_place = final_and_third_place_df.apply(
        lambda row: decide_winner_knockout_phase_elo(row, team_elos, rng=rng), axis=1
    )
    results_final_and_third_place = pd.DataFrame(results_final_and_third_place.tolist())

    results_knockout_phase = pd.concat([results_knockout_games_df, results_knockout_games_round_of_16, results_quarterfinals, results_semifinals, results_final_and_third_place], axis=0)
    results_knockout_phase["draw"] = (results_knockout_phase["home_goals"] == results_knockout_phase["away_goals"]).astype(int)
    knockout_team_points = sum_knockout_points_by_team(results_knockout_phase)
    # Apply the function to calculate points_home and points_away
    fixtures_df['points_home'] = fixtures_df.apply(
        lambda row: calculate_points(
            goals_scored=row['home_goals'],
            goals_conceded=row['away_goals'],
            is_winner=(row['result'] == 'home'),
            is_draw=(row['result'] == 'draw')
        ), axis=1
    )

    fixtures_df['points_away'] = fixtures_df.apply(
        lambda row: calculate_points(
            goals_scored=row['away_goals'],
            goals_conceded=row['home_goals'],
            is_winner=(row['result'] == 'away'),
            is_draw=(row['result'] == 'draw')
        ), axis=1
    )

    team_points = sum_points_by_team(fixtures_df)

    total_standings = combine_total_points(team_points, knockout_team_points)
    print(total_standings)
    
    # Extract and compare ELO ratings
    elo_comparison = extract_final_elos(fixtures_df, results_knockout_phase)
    print("\n=== ELO Rating Evolution ===")
    print(elo_comparison.to_string(index=False))

    print("------------Group phase-------------")
    print(standings_df)
    print("-------------Knockout phase------------")
    print(results_knockout_phase[["nb", "home", "away", "home_goals", "away_goals", "result"]])