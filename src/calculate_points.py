import pandas as pd


def calculate_points(goals_scored, goals_conceded, is_winner, is_draw):
    points = 0
    # Win
    if is_winner:
        points += 3
    # Draw
    elif is_draw:
        points += 1

    # No goals conceded
    if goals_conceded == 0:
        points += 1

    # Scored 3 or more goals
    if goals_scored >= 3:
        points += 1

    return points

def sum_points_by_team(fixtures_df: pd.DataFrame) -> pd.DataFrame:
    """
    Sum up all the points for each team across the entire fixtures DataFrame.

    Args:
        fixtures_df: DataFrame with columns 'home', 'away', 'points_home', 'points_away'.

    Returns:
        DataFrame with columns 'team' and 'total_points', sorted by total_points (descending).
    """
    # Melt the DataFrame to combine home and away teams
    home_df = fixtures_df[['home', 'points_home']].rename(columns={'home': 'team', 'points_home': 'points'})
    away_df = fixtures_df[['away', 'points_away']].rename(columns={'away': 'team', 'points_away': 'points'})

    # Combine home and away DataFrames
    all_points = pd.concat([home_df, away_df])

    # Group by team and sum the points
    total_points = all_points.groupby('team')['points'].sum().reset_index()
    total_points = total_points.rename(columns={'points': 'total_points'})

    # Sort by total_points (descending)
    total_points = total_points.sort_values('total_points', ascending=False)

    return total_points

def sum_knockout_points_by_team(results_knockout_phase: pd.DataFrame) -> pd.DataFrame:
    """
    Sum up all the points for each team across the knockout phase results.
    Handles draws (including penalty shootouts) by checking the 'draw' column.

    Args:
        results_knockout_phase: DataFrame with columns 'nb', 'home', 'away', 'home_goals', 'away_goals', 'result', 'draw'.

    Returns:
        DataFrame with columns 'team' and 'total_points', sorted by total_points (descending).
    """
    points_list = []

    for _, row in results_knockout_phase.iterrows():
        home = row['home']
        away = row['away']
        home_goals = row['home_goals']
        away_goals = row['away_goals']
        winner = row['result']
        is_draw = row['draw']  # 1 if draw, 0 otherwise

        # Determine points for home team
        home_points = 0
        if is_draw:
            home_points += 1  # Draw
        elif winner == home:
            home_points += 3  # Win
        # Else: Loss (0 points)

        # No goals conceded
        if away_goals == 0:
            home_points += 1

        # Scored 3 or more goals
        if home_goals >= 3:
            home_points += 1

        # Determine points for away team
        away_points = 0
        if is_draw:
            away_points += 1  # Draw
        elif winner == away:
            away_points += 3  # Win
        # Else: Loss (0 points)

        # No goals conceded
        if home_goals == 0:
            away_points += 1

        # Scored 3 or more goals
        if away_goals >= 3:
            away_points += 1

        # Append points for both teams
        points_list.append({'team': home, 'points': home_points})
        points_list.append({'team': away, 'points': away_points})

    # Create a DataFrame from the list
    points_df = pd.DataFrame(points_list)

    # Sum points by team
    total_points = points_df.groupby('team')['points'].sum().reset_index()
    total_points = total_points.rename(columns={'points': 'total_points'})

    # Sort by total_points (descending)
    total_points = total_points.sort_values('total_points', ascending=False)

    return total_points


def combine_total_points(
        group_points: pd.DataFrame,
        knockout_points: pd.DataFrame
    ) -> pd.DataFrame:
    """
    Combine group stage and knockout phase points for each team.

    Args:
        group_points: DataFrame with columns 'team' and 'total_points' (from group stage).
        knockout_points: DataFrame with columns 'team' and 'total_points' (from knockout phase).

    Returns:
        DataFrame with columns 'team' and 'total_points', sorted by total_points (descending).
    """
    # Merge the two DataFrames on 'team' with an outer join
    combined = pd.merge(
        group_points,
        knockout_points,
        on='team',
        how='outer',
        suffixes=('_group', '_knockout')
    )

    # Fill NaN values with 0 (for teams that didn't participate in one of the phases)
    combined = combined.fillna(0)

    # Sum the points from both phases
    combined['total_points'] = combined['total_points_group'] + combined['total_points_knockout']

    # Select and sort the final columns
    total_standings = combined[['team', 'total_points']].sort_values('total_points', ascending=False)

    return total_standings