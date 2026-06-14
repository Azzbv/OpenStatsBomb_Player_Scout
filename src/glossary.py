def get_metric_glossary():
    """Return dictionary of metric definitions for user education."""
    return {
        "goals": {
            "display": "Goals",
            "category": "Attacking",
            "definition": "Total goals scored by the player.",
            "rationale": "Primary output for forwards.",
            "method": "Count of 'Shot' events with outcome 'Goal'.",
            "note": "Exact measure."
        },
        "np_goals": {
            "display": "Non-Penalty Goals",
            "category": "Attacking",
            "definition": "Goals scored excluding penalty kicks.",
            "rationale": "Better indicator of open-play finishing sustainability.",
            "method": "Goals where shot_type is not 'Penalty'.",
            "note": "Exact measure."
        },
        "shots": {
            "display": "Shots",
            "category": "Attacking",
            "definition": "Total shot attempts.",
            "rationale": "Indicates goal-scoring intent and volume.",
            "method": "Count of all 'Shot' events.",
            "note": "Exact measure."
        },
        "shots_on_target": {
            "display": "Shots on Target",
            "category": "Attacking",
            "definition": "Shots that were either goals or saved by the keeper.",
            "rationale": "Measures shooting accuracy and threat.",
            "method": "Shots with outcome 'Goal', 'Saved', or 'Saved to Post'.",
            "note": "Exact measure."
        },
        "np_shots": {
            "display": "Non-Penalty Shots",
            "category": "Attacking",
            "definition": "Shot attempts excluding penalty kicks.",
            "rationale": "Open-play/set-piece shot volume without penalty inflation.",
            "method": "Count of 'Shot' events where shot_type is not 'Penalty'.",
            "note": "Exact measure."
        },
        "np_shots_on_target": {
            "display": "Non-Penalty Shots on Target",
            "category": "Attacking",
            "definition": "On-target shots excluding penalty kicks.",
            "rationale": "Accuracy/threat volume independent of penalties.",
            "method": "Non-penalty shots with outcome 'Goal', 'Saved', or 'Saved to Post'.",
            "note": "Exact measure."
        },
        "xg": {
            "display": "Expected Goals (xG)",
            "category": "Attacking",
            "definition": "The probability that a shot will result in a goal based on historical data.",
            "rationale": "Measures quality of chances created/received.",
            "method": "Sum of 'shot_statsbomb_xg' values.",
            "note": "StatsBomb internal model."
        },
        "np_xg": {
            "display": "Non-Penalty xG",
            "category": "Attacking",
            "definition": "Expected goals excluding penalty kicks.",
            "rationale": "Filters out high-probability set-piece variance.",
            "method": "xG sum where shot_type is not 'Penalty'.",
            "note": "StatsBomb internal model."
        },
        "xg_per_shot": {
            "display": "xG per Shot",
            "category": "Attacking",
            "definition": "Average quality of shots taken.",
            "rationale": "High value indicates elite shot selection (shooting from better positions).",
            "method": "Non-penalty xG / Non-penalty shots.",
            "note": "Exact measure."
        },
        "passes_f3": {
            "display": "Passes into Final Third",
            "category": "Progression",
            "definition": "Completed passes entering the attacking third.",
            "rationale": "Shows ability to move team into dangerous zones.",
            "method": "End X > 80, Start X < 80.",
            "note": "Exact measure."
        },
        "passes_pa": {
            "display": "Passes into Penalty Area",
            "category": "Progression",
            "definition": "Completed passes entering the opposition box.",
            "rationale": "Elite indicator of chance creation and penetration.",
            "method": "End X > 102, 18 < End Y < 62.",
            "note": "Exact measure."
        },
        "prog_passes": {
            "display": "Progressive Passes",
            "category": "Progression",
            "definition": "Passes that move the ball significantly closer to goal.",
            "rationale": "Measures verticality and line-breaking ability.",
            "method": "Pass end location > 12m closer to goal line than start.",
            "note": "Positional proxy."
        },
        "prog_carries": {
            "display": "Progressive Carries",
            "category": "Progression",
            "definition": "Ball carries that move significantly closer to goal.",
            "rationale": "Shows ability to drive forward and beat lines with the ball.",
            "method": "Carry end location > 10m closer to goal line than start.",
            "note": "Positional proxy."
        },
        "key_passes": {
            "display": "Key Passes",
            "category": "Creativity",
            "definition": "Passes leading directly to a shot.",
            "rationale": "Immediate creative output indicator.",
            "method": "Passes with 'shot_assist' or 'goal_assist' flags.",
            "note": "Exact measure."
        },
        "assists": {
            "display": "Assists",
            "category": "Creativity",
            "definition": "Passes leading directly to a goal.",
            "rationale": "Direct contribution to scoring.",
            "method": "Passes with 'goal_assist' flag.",
            "note": "Exact measure."
        },
        "dribbles": {
            "display": "Dribbles Completed",
            "category": "Creativity",
            "definition": "Successful take-ons while in possession.",
            "rationale": "Shows 1v1 ability and ball retention under pressure.",
            "method": "Count of 'Dribble' events with outcome 'Complete'.",
            "note": "Exact measure."
        },
        "passes": {
            "display": "Passes Attempted",
            "category": "Possession",
            "definition": "Total number of passes attempted.",
            "rationale": "Shows involvement level in build-up.",
            "method": "Count of all 'Pass' events.",
            "note": "Exact measure."
        },
        "passes_completed": {
            "display": "Passes Completed",
            "category": "Possession",
            "definition": "Total number of successful passes.",
            "rationale": "Measures reliable possession contribution.",
            "method": "Pass events with no 'outcome' (successful).",
            "note": "Exact measure."
        },
        "pass_completion_pct": {
            "display": "Pass Completion %",
            "category": "Possession",
            "definition": "Percentage of attempted passes that were successful.",
            "rationale": "Indicates passing accuracy and technical security.",
            "method": "(Completed / Attempted) * 100.",
            "note": "Exact measure."
        },
        "turnovers": {
            "display": "Turnovers",
            "category": "Possession",
            "definition": "Total losses of possession.",
            "rationale": "Indicates risk-taking or technical instability.",
            "method": "Sum of 'Miscontrol' and 'Dispossessed' events.",
            "note": "Exact measure."
        },
        "pressures": {
            "display": "Pressures",
            "category": "Defending",
            "definition": "Number of times a player pressured an opponent in possession.",
            "rationale": "Work-rate and defensive intensity indicator.",
            "method": "Count of 'Pressure' events.",
            "note": "Exact measure."
        },
        "tackles": {
            "display": "Tackles",
            "category": "Defending",
            "definition": "Defensive attempts to dispossess an opponent.",
            "rationale": "Key indicator of active defensive involvement.",
            "method": "Count of 'Duel' events with type 'Tackle'.",
            "note": "Exact measure."
        },
        "interceptions": {
            "display": "Interceptions",
            "category": "Defending",
            "definition": "Cutting off an opponent's pass.",
            "rationale": "Measures anticipation and defensive positioning.",
            "method": "Count of 'Interception' events.",
            "note": "Exact measure."
        },
        "recoveries": {
            "display": "Recoveries",
            "category": "Defending",
            "definition": "Winning back loose balls.",
            "rationale": "Ability to clean up second balls and regain control.",
            "method": "Count of 'Ball Recovery' events.",
            "note": "Exact measure."
        },
        "blocks": {
            "display": "Blocks",
            "category": "Defending",
            "definition": "Blocking an opponent's pass or shot attempt.",
            "rationale": "Defensive resilience and grit.",
            "method": "Count of 'Block' events.",
            "note": "Exact measure."
        },
        "scout_score": {
            "display": "Fit Score",
            "category": "Scoring",
            "definition": "Weighted tactical ranking (0-100).",
            "rationale": "Allows role-specific player evaluation.",
            "method": "Weighted sum of normalized per-90 KPIs.",
            "note": "Analytic model."
        }
    }
