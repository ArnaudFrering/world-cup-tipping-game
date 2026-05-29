import pandas as pd
import json

def extract_final_elos(fixtures_df, results_knockout_phase, initial_elos_path='data/first_elo scores.json'):
    """
    Extract the final ELO ratings of each team from the competition and compare with initial values.
    
    Args:
        fixtures_df: DataFrame with group stage results containing home_elo and away_elo columns
        results_knockout_phase: DataFrame with knockout stage results containing home_elo_new and away_elo_new columns
        initial_elos_path: Path to the initial ELO ratings JSON file
    
    Returns:
        DataFrame with columns: team, initial_elo, final_elo, elo_change
    """
    # Load initial ELOs
    with open(initial_elos_path) as f:
        initial_elos = json.load(f)
    
    final_elos = {}
    
    # Extract final ELOs from group stage (fixtures_df)
    for team in initial_elos.keys():
        # Find last occurrence of team as home
        home_matches = fixtures_df[fixtures_df['home'] == team]
        if not home_matches.empty:
            final_elos[team] = home_matches.iloc[-1]['home_elo']
        
        # Find last occurrence of team as away and override if more recent
        away_matches = fixtures_df[fixtures_df['away'] == team]
        if not away_matches.empty:
            final_elos[team] = away_matches.iloc[-1]['away_elo']
    
    # Extract final ELOs from knockout stage (results_knockout_phase) if team participated
    for team in initial_elos.keys():
        # Find last occurrence of team as home
        home_matches = results_knockout_phase[results_knockout_phase['home'] == team]
        if not home_matches.empty:
            final_elos[team] = home_matches.iloc[-1]['home_elo_new']
        
        # Find last occurrence of team as away and override if more recent
        away_matches = results_knockout_phase[results_knockout_phase['away'] == team]
        if not away_matches.empty:
            final_elos[team] = away_matches.iloc[-1]['away_elo_new']
    
    # Create comparison DataFrame
    comparison_data = []
    for team in sorted(initial_elos.keys()):
        initial = initial_elos[team]
        final = final_elos.get(team, initial)  # If team not in results, use initial
        change = final - initial
        
        comparison_data.append({
            'Team': team,
            'Initial ELO': initial,
            'Final ELO': final,
            'ELO Change': change
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df = comparison_df.sort_values('ELO Change', ascending=False)
    
    return comparison_df