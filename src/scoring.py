import pandas as pd
import numpy as np

def get_role_templates():
    return {
        "Ball-Playing Centre Back": {
            "passes_completed_per90": 10,
            "prog_passes_per90": 9,
            "pass_completion_pct": 8,
            "interceptions_per90": 6,
            "recoveries_per90": 5,
            "blocks_per90": 4,
            "passes_f3_per90": 5
        },
        "Libero / Sweeper Keeper": {
            "passes_completed_per90": 10,
            "pass_completion_pct": 9,
            "prog_passes_per90": 7,
            "recoveries_per90": 8,
            "interceptions_per90": 5
        },
        "Inverted Full Back": {
            "passes_completed_per90": 10,
            "pass_completion_pct": 9,
            "prog_passes_per90": 8,
            "interceptions_per90": 7,
            "recoveries_per90": 6,
            "passes_f3_per90": 7
        },
        "Offensive Wing Back": {
            "prog_carries_per90": 10,
            "prog_passes_per90": 8,
            "passes_pa_per90": 9,
            "dribbles_per90": 8,
            "key_passes_per90": 7,
            "assists_per90": 6
        },
        "Defensive Anchor (No. 6)": {
            "interceptions_per90": 10,
            "tackles_per90": 9,
            "pressures_per90": 8,
            "recoveries_per90": 9,
            "blocks_per90": 7,
            "pass_completion_pct": 8
        },
        "Deep-Lying Playmaker": {
            "prog_passes_per90": 10,
            "passes_completed_per90": 10,
            "passes_f3_per90": 9,
            "pass_completion_pct": 8,
            "key_passes_per90": 6,
            "recoveries_per90": 5
        },
        "Box-to-Box Midfielder (No. 8)": {
            "pressures_per90": 9,
            "recoveries_per90": 9,
            "prog_passes_per90": 8,
            "prog_carries_per90": 8,
            "shots_per90": 6,
            "tackles_per90": 7,
            "passes_f3_per90": 7
        },
        "Mezzala / Creative 8": {
            "key_passes_per90": 10,
            "prog_passes_per90": 9,
            "passes_pa_per90": 9,
            "dribbles_per90": 8,
            "assists_per90": 7,
            "np_xg_per90": 6
        },
        "Classic Winger": {
            "dribbles_per90": 10,
            "prog_carries_per90": 9,
            "passes_pa_per90": 10,
            "key_passes_per90": 8,
            "assists_per90": 7
        },
        "Inverted Winger / Inside Forward": {
            "np_xg_per90": 10,
            "shots_per90": 9,
            "shots_on_target_per90": 8,
            "dribbles_per90": 9,
            "key_passes_per90": 7,
            "prog_carries_per90": 8
        },
        "Shadow Striker (No. 10)": {
            "np_xg_per90": 10,
            "shots_per90": 9,
            "key_passes_per90": 10,
            "assists_per90": 8,
            "passes_pa_per90": 8,
            "turnovers_per90": -3
        },
        "Pressing Forward": {
            "pressures_per90": 10,
            "recoveries_per90": 9,
            "tackles_per90": 7,
            "np_xg_per90": 9,
            "shots_per90": 8,
            "interceptions_per90": 6
        },
        "Target Man / Target Forward": {
            "shots_per90": 9,
            "np_xg_per90": 8,
            "passes_pa_per90": 6,
            "key_passes_per90": 6,
            "blocks_per90": 4, # Helping at set pieces
            "shots_on_target_per90": 8
        },
        "False Nine": {
            "key_passes_per90": 10,
            "assists_per90": 8,
            "prog_passes_per90": 9,
            "passes_f3_per90": 8,
            "np_xg_per90": 7,
            "dribbles_per90": 7
        }
    }

def calculate_recruitment_score(df_norm, weights):
    df = df_norm.copy()
    total_abs_weight = sum(abs(v) for v in weights.values())
    
    if total_abs_weight == 0:
        df["scout_score"] = 0.0
        return df

    for metric, weight in weights.items():
        norm_col = f"{metric}_norm"
        if norm_col in df.columns:
            df[f"{metric}_contrib"] = (df[norm_col] * weight) / total_abs_weight
        else:
            df[f"{metric}_contrib"] = 0.0

    contrib_cols = [f"{m}_contrib" for m in weights.keys()]
    df["scout_score"] = df[contrib_cols].sum(axis=1) * 100
    df["scout_score"] = df["scout_score"].clip(0, 100)
    
    return df

def get_fit_breakdown(player_row, weights):
    breakdown = {}
    for m in weights.keys():
        contrib = player_row.get(f"{m}_contrib", 0) * 100
        breakdown[m] = contrib
    
    return dict(sorted(breakdown.items(), key=lambda x: abs(x[1]), reverse=True))
