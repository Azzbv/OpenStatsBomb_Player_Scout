import pandas as pd

def map_positions_to_roles(df, pos_col="pos"):
    role_map = {
        'Center Back': 'Centre Back',
        'CB': 'Centre Back',
        'Left Back': 'Full Back / Wing Back',
        'Right Back': 'Full Back / Wing Back',
        'LB': 'Full Back / Wing Back',
        'RB': 'Full Back / Wing Back',
        'WB': 'Full Back / Wing Back',
        'Left Wing Back': 'Full Back / Wing Back',
        'Right Wing Back': 'Full Back / Wing Back',
        'Defensive Midfield': 'Defensive Midfielder',
        'DM': 'Defensive Midfielder',
        'Center Midfield': 'Central Midfielder',
        'CM': 'Central Midfielder',
        'Attacking Midfield': 'Attacking Midfielder / Winger',
        'AM': 'Attacking Midfielder / Winger',
        'Left Wing': 'Attacking Midfielder / Winger',
        'Right Wing': 'Attacking Midfielder / Winger',
        'LW': 'Attacking Midfielder / Winger',
        'RW': 'Attacking Midfielder / Winger',
        'Center Forward': 'Forward',
        'ST': 'Forward',
        'CF': 'Forward',
        'Goalkeeper': 'Goalkeeper',
        'GK': 'Goalkeeper'
    }
    df = df.copy()
    df['role_group'] = df[pos_col].map(role_map).fillna('Other')
    return df

def filter_by_minutes(df, min_minutes=450, minutes_col="minutes"):
    return df[df[minutes_col] >= min_minutes].copy()

def filter_by_matches(df, min_matches=3, matches_col="matches"):
    return df[df[matches_col] >= min_matches].copy()

def filter_players(df, position=None, role_group=None, age_range=None):
    filtered_df = df.copy()
    if position:
        filtered_df = filtered_df[filtered_df["pos"] == position]
    if role_group:
        filtered_df = filtered_df[filtered_df["role_group"] == role_group]
    if age_range:
        filtered_df = filtered_df[
            (filtered_df["age"] >= age_range[0]) & 
            (filtered_df["age"] <= age_range[1])
        ]
    return filtered_df

def normalize_metrics(df, metrics):
    df_norm = df.copy()
    for m in metrics:
        if m in df.columns:
            df_norm[f"{m}_norm"] = df[m].rank(pct=True, method='min')
        else:
            df_norm[f"{m}_norm"] = 0.0
    return df_norm
