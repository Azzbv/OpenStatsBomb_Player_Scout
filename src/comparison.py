import pandas as pd
from src.style import safe

def get_best_in_categories(df, metrics_by_cat):
    """Identify which player leads in each category."""
    highlights = {}
    for cat, metrics in metrics_by_cat.items():
        valid_metrics = [m for m in metrics if m in df.columns]
        if not valid_metrics:
            continue

        leaders = []
        for m in valid_metrics:
            col = df[m]
            if col.notna().any():  # idxmax raises on an all-NaN/empty column
                leaders.append(df.loc[col.idxmax(), "player"])

        if leaders:
            highlights[cat] = max(set(leaders), key=leaders.count)
    return highlights

def generate_scouting_note(player_row, role_weights, metrics_by_cat):
    """Generate a concise, professional scouting note."""
    player = player_row["player"]
    score = player_row["scout_score"]

    cat_scores = {}
    for cat, metrics in metrics_by_cat.items():
        valid = [f"{m}_norm" for m in metrics if f"{m}_norm" in player_row.index]
        if valid:
            cat_scores[cat] = player_row[valid].mean()

    top_cats = sorted(cat_scores.items(), key=lambda x: x[1], reverse=True)[:2]
    cat_str = " and ".join([c[0].lower() for c in top_cats])

    top_metric = "N/A"
    norm_cols = [c for c in player_row.index if c.endswith("_norm")]
    if norm_cols:
        top_metric_col = player_row[norm_cols].idxmax().replace("_norm", "").replace("_", " ").title()
        top_metric = top_metric_col

    # Escape data-derived values before they reach HTML-capable markdown sinks.
    note = (
        f"**{safe(player)}** (Fit: {score:.1f}/100). "
        f"Strongest in {safe(cat_str)}. "
        f"Standout metric: {safe(top_metric)}. "
        f"Profile suggests high suitability for required tactical outputs."
    )
    return note
