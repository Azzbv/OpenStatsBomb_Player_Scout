import pandas as pd
import numpy as np

def get_top_traits(player_row, metrics, threshold=0.75):
    """Identify metrics where player is in top percentile."""
    traits = []
    for m in metrics:
        norm_col = f"{m}_norm"
        if norm_col in player_row and player_row[norm_col] >= threshold:
            traits.append(m.replace("_", " ").title())
    return traits

def generate_recruitment_report(player_row, metrics_by_cat, all_metrics):
    """
    Generate professional recruitment insights based on real match events.
    """
    player = player_row["player"]
    role = player_row["role_group"]
    
    # 1. Profile Summary (Based on top category)
    cat_performance = {}
    for cat, ms in metrics_by_cat.items():
        norms = [f"{m}_norm" for m in ms if f"{m}_norm" in player_row.index]
        if norms:
            cat_performance[cat] = player_row[norms].mean()
            
    top_cat = max(cat_performance, key=cat_performance.get) if cat_performance else "Balanced"
    
    # Sector specific summary
    if player_row.get('final_third_ratio', 0) > 0.4:
        loc_desc = "high final-third involvement"
    elif player_row.get('actions_mid', 0) > player_row.get('actions_final', 0):
        loc_desc = "central/middle-third heavy profile"
    else:
        loc_desc = "balanced spatial footprint"

    summary = f"Modern {role.lower()} exhibiting a {top_cat.lower()}-centric profile with {loc_desc}."

    # 2. Strengths (Top 20% performance)
    strengths = []
    for m in all_metrics:
        norm_col = f"{m}_norm"
        if norm_col in player_row and player_row[norm_col] >= 0.80:
            name = m.replace("_per90", "").replace("_", " ").title()
            strengths.append(name)
            
    # 3. Risks (Bottom 20% performance)
    risks = []
    for m in all_metrics:
        norm_col = f"{m}_norm"
        if norm_col in player_row and player_row[norm_col] <= 0.20:
            name = m.replace("_per90", "").replace("_", " ").title()
            risks.append(name)

    # 4. Likely Role Fit (Specific tactical niches)
    role_fit = ""
    if cat_performance.get("Progression", 0) > 0.7:
        role_fit = "Primary ball progressor suited for transition-heavy systems."
    elif cat_performance.get("Creativity", 0) > 0.7:
        role_fit = "Creative hub capable of operating in congested final-third zones."
    elif cat_performance.get("Defending", 0) > 0.7:
        role_fit = "Defensive anchor with high-intensity pressing and recovery volume."
    else:
        role_fit = f"Reliable {role.lower()} with consistent output in {top_cat.lower()} actions."

    # 5. Recommendation Note
    score = player_row["scout_score"]
    if score >= 80:
        rec = "High-priority target. Profile matches elite benchmarks for chosen tactical role."
    elif score >= 60:
        rec = "Recommended squad option. Specialized profile with clear tactical utility."
    elif score >= 40:
        rec = "Monitor. Displays specific strengths but lacks consistent volume across all role KPIs."
    else:
        rec = "Niche / developmental prospect. Requires specific tactical context to succeed."

    return {
        "summary": summary,
        "strengths": strengths[:4] if strengths else ["Consistent across core metrics"],
        "risks": risks[:4] if risks else ["Low statistical volatility"],
        "role_fit": role_fit,
        "recommendation": rec
    }

def generate_tldr_summary(player_row, metrics_by_cat):
    """
    Generate a compact, coach-friendly TL;DR summary card.
    """
    # 1. Profile Synthesis
    role = player_row["role_group"]
    cat_scores = {}
    for cat, ms in metrics_by_cat.items():
        norms = [f"{m}_norm" for m in ms if f"{m}_norm" in player_row.index]
        if norms: cat_scores[cat] = player_row[norms].mean()
    
    top_cat = max(cat_scores, key=cat_scores.get) if cat_scores else "Balanced"
    profile_note = f"{top_cat}-oriented {role.lower()} with {'high' if player_row.get('final_third_ratio', 0) > 0.35 else 'balanced'} field involvement."

    # 2. Advantages (Top 15% metrics)
    adv = []
    for m in player_row.index:
        if m.endswith("_norm") and player_row[m] >= 0.85:
            adv.append(m.replace("_norm", "").replace("_per90", "").replace("_", " ").title())
    
    # 3. Weaknesses (Bottom 15% metrics)
    weak = []
    for m in player_row.index:
        if m.endswith("_norm") and player_row[m] <= 0.15:
            weak.append(m.replace("_norm", "").replace("_per90", "").replace("_", " ").title())

    # 4. Tactical Fit
    fit_note = "Suited for "
    if cat_scores.get("Progression", 0) > 0.6: fit_note += "possession-heavy systems needing line-breaking actions."
    elif cat_scores.get("Defending", 0) > 0.6: fit_note += "high-intensity pressing structures."
    elif cat_scores.get("Attacking", 0) > 0.6: fit_note += "systems requiring high-volume final-third threat."
    else: fit_note += "balanced tactical setups."

    return {
        "profile": profile_note,
        "advantages": ", ".join(adv[:3]) if adv else "Reliable volume across role KPIs",
        "weaknesses": ", ".join(weak[:3]) if weak else "No significant statistical red flags",
        "fit": fit_note
    }
