import pandas as pd

def get_best_in_categories(df, metrics_by_cat):
    """Identify which player leads in each category."""
    highlights = {}
    for cat, metrics in metrics_by_cat.items():
        # Only use metrics present in the comparison
        valid_metrics = [m for m in metrics if m in df.columns]
        if not valid_metrics:
            continue
        
        # Calculate category average or leader
        # For simplicity, we find the player who leads the most metrics in the category
        leaders = []
        for m in valid_metrics:
            leader = df.loc[df[m].idxmax(), "player"]
            leaders.append(leader)
        
        # Most frequent leader in category
        highlights[cat] = max(set(leaders), key=leaders.count)
    return highlights

def generate_scouting_note(player_row, role_weights, metrics_by_cat):
    """Generate a concise, professional scouting note."""
    player = player_row["player"]
    score = player_row["scout_score"]
    
    # Identify top 2 categories
    cat_scores = {}
    for cat, metrics in metrics_by_cat.items():
        valid = [f"{m}_norm" for m in metrics if f"{m}_norm" in player_row.index]
        if valid:
            cat_scores[cat] = player_row[valid].mean()
    
    top_cats = sorted(cat_scores.items(), key=lambda x: x[1], reverse=True)[:2]
    cat_str = " and ".join([c[0].lower() for c in top_cats])
    
    # Identify top metric
    top_metric = "N/A"
    norm_cols = [c for c in player_row.index if c.endswith("_norm")]
    if norm_cols:
        top_metric_col = player_row[norm_cols].idxmax().replace("_norm", "").replace("_", " ").title()
        top_metric = top_metric_col

    note = (
        f"**{player}** (Fit: {score:.1f}/100). "
        f"Strongest in {cat_str}. "
        f"Standout metric: {top_metric}. "
        f"Profile suggests high suitability for required tactical outputs."
    )
    return note
