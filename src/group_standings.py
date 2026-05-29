import pandas as pd
from typing import Dict, Any, List

def compute_group_standings(fixtures_df: pd.DataFrame,
                            win_points: int = 3,
                            draw_points: int = 1,
                            loss_points: int = 0) -> pd.DataFrame:
    """
    Transform a fixtures/results DataFrame into group standings.

    fixtures_df must have columns: ['group', 'home', 'away', 'home_goals', 'away_goals']

    Returns a DataFrame with columns:
      ['group', 'team', 'played', 'wins', 'draws', 'losses',
       'goals_for', 'goals_against', 'goal_diff', 'points']
    Sorted by group and applying tie-breakers:
      1) Most points
      2) Overall goal difference
      3) Overall goals scored
      4) Team name (asc)
    """
    stats: Dict[str, Dict[str, Any]] = {}

    def ensure(team: str, group: str):
        key = (group, team)
        if key not in stats:
            stats[key] = {
                "group": group,
                "team": team,
                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "points": 0,
            }
        return stats[key]

    for _, row in fixtures_df.iterrows():
        group = row["group"]
        home = row["home"]
        away = row["away"]
        hg = int(row.get("home_goals", 0))
        ag = int(row.get("away_goals", 0))

        sh = ensure(home, group)
        sa = ensure(away, group)

        sh["played"] += 1
        sa["played"] += 1

        sh["goals_for"] += hg
        sh["goals_against"] += ag

        sa["goals_for"] += ag
        sa["goals_against"] += hg

        if hg > ag:
            sh["wins"] += 1
            sa["losses"] += 1
            sh["points"] += win_points
            sa["points"] += loss_points
        elif hg < ag:
            sa["wins"] += 1
            sh["losses"] += 1
            sa["points"] += win_points
            sh["points"] += loss_points
        else:
            sh["draws"] += 1
            sa["draws"] += 1
            sh["points"] += draw_points
            sa["points"] += draw_points

    # prepare overall rows and groups
    overall: Dict[str, Dict[str, Any]] = {}
    groups: Dict[str, List[str]] = {}
    for (group, team), v in stats.items():
        v["goal_diff"] = v["goals_for"] - v["goals_against"]
        overall.setdefault(group, {})[team] = v
        groups.setdefault(group, []).append(team)

    rows = []

    # For each group sort by: points desc, goal_diff desc, goals_for desc, team asc
    for group, teams in groups.items():
        teams_sorted = sorted(
            teams,
            key=lambda t: (
                -overall[group][t]["points"],
                -overall[group][t]["goal_diff"],
                -overall[group][t]["goals_for"],
                t
            )
        )
        for pos, t in enumerate(teams_sorted, start=1):
            row = overall[group][t].copy()
            row["position_in_the_group"] = pos
            rows.append(row)


    df = pd.DataFrame(rows, columns=[
        "group", "team", "played", "wins", "draws", "losses",
        "goals_for", "goals_against", "goal_diff", "points", "position_in_the_group"
    ])

    df = df.reset_index(drop=True)
    df["group_letter"] = df["group"].str.split(" ").str[1]
    df["group_and_position"] = df["position_in_the_group"].astype(str)+df["group_letter"]
    return df


def standings_between_thirds(standings_df: pd.DataFrame) -> pd.DataFrame:
    # Filter teams in 3rd position
    thirds = standings_df[standings_df["position_in_the_group"] == 3].copy()

    # Sort by the required criteria
    thirds_sorted = thirds.sort_values(
        by=["points", "goal_diff", "goals_for"],
        ascending=[False, False, False]
    )

    # Return the top 8 rows
    return thirds_sorted.head(8)
