import pandas as pd
import numpy as np

def calculate_scouting_metrics(df):
    df = df.copy()
    safe_mins = df["minutes"].replace(0, 1)
    
    p90_cols = [
        "goals", "np_goals", "shots", "shots_on_target", "xg", "np_xg", 
        "assists", "key_passes", "passes", "passes_completed", 
        "passes_f3", "passes_pa", "prog_passes",
        "carries", "prog_carries", "dribbles", "turnovers",
        "pressures", "tackles", "interceptions", "recoveries", "blocks"
    ]
    
    for col in p90_cols:
        if col in df.columns:
            df[f"{col}_per90"] = (df[col] / safe_mins) * 90
            
    if "passes" in df.columns and "passes_completed" in df.columns:
        df["pass_completion_pct"] = (df["passes_completed"] / df["passes"].replace(0, 1)) * 100
        
    return df

def get_metric_categories():
    return {
        "Attacking": ["goals_per90", "np_goals_per90", "shots_per90", "xg_per90", "np_xg_per90", "xg_per_shot"],
        "Progression": ["prog_passes_per90", "prog_carries_per90", "passes_f3_per90", "passes_pa_per90"],
        "Creativity": ["assists_per90", "key_passes_per90", "dribbles_per90"],
        "Possession": ["pass_completion_pct", "turnovers_per90"],
        "Defending": ["pressures_per90", "tackles_per90", "interceptions_per90", "recoveries_per90", "blocks_per90"]
    }
