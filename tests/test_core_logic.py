import pandas as pd
import numpy as np
import pytest
from unittest.mock import patch
from src.metrics import calculate_scouting_metrics
from src.scoring import calculate_recruitment_score, get_role_templates
from src.transforms import normalize_metrics
from src.data_loader import _process_match_events

def test_calculate_scouting_metrics():
    data = {
        "player": ["Player A"],
        "minutes": [90],
        "goals": [1],
        "passes": [100],
        "passes_completed": [80]
    }
    df = pd.DataFrame(data)
    df_result = calculate_scouting_metrics(df)
    
    assert df_result.iloc[0]["goals_per90"] == 1.0
    assert df_result.iloc[0]["pass_completion_pct"] == 80.0

def test_normalize_metrics():
    data = {
        "val": [10, 20, 30]
    }
    df = pd.DataFrame(data)
    df_norm = normalize_metrics(df, ["val"])

    # normalize_metrics uses rank(pct=True, method='min'): the lowest of n values
    # maps to 1/n (not 0), the highest to 1.0. Percentile rank is intentionally
    # outlier-robust (standard for scouting percentiles), unlike min-max scaling.
    assert df_norm["val_norm"].max() == 1.0
    assert df_norm["val_norm"].iloc[0] == pytest.approx(1 / 3)
    assert df_norm["val_norm"].iloc[1] == pytest.approx(2 / 3)

def test_scoring_logic():
    data = {
        "m1_norm": [1.0, 0.5, 0.0],
        "m2_norm": [0.0, 0.5, 1.0]
    }
    df = pd.DataFrame(data)
    weights = {"m1": 10, "m2": 5}
    
    scored_df = calculate_recruitment_score(df, weights)
    
    # Total weight = 15
    # Row 0: (1.0*10 + 0.0*5)/15 = 10/15 = 0.66... * 100 = 66.7
    assert pytest.approx(scored_df.iloc[0]["scout_score"], 0.1) == 66.7
    # Row 1: (0.5*10 + 0.5*5)/15 = 7.5/15 = 0.5 * 100 = 50.0
    assert scored_df.iloc[1]["scout_score"] == 50.0

def _run_events(event_rows):
    """Drive _process_match_events with a mocked sb.events frame for one player."""
    pid = 99
    player_agg = {pid: {
        "player": "P", "team": "T",
        "goals": 0, "np_goals": 0, "shots": 0, "shots_on_target": 0,
        "np_shots": 0, "np_shots_on_target": 0,
        "xg": 0.0, "np_xg": 0.0, "assists": 0, "key_passes": 0,
        "passes": 0, "passes_completed": 0, "passes_f3": 0, "passes_pa": 0,
        "prog_passes": 0, "carries": 0, "prog_carries": 0, "dribbles": 0,
        "dispossessions": 0, "miscontrols": 0, "pressures": 0, "tackles": 0,
        "interceptions": 0, "recoveries": 0, "blocks": 0,
    }}
    player_events = {pid: []}
    frame = pd.DataFrame([{"player_id": pid, **row} for row in event_rows])
    with patch("src.data_loader.sb.events", return_value=frame):
        _process_match_events("m1", player_agg, player_events)
    return player_agg[pid]


def test_ball_recovery_increments_recoveries():
    # Regression for the chained-ternary bug that produced 'ball_recoverys'
    # and left 'recoveries' permanently at 0.
    stats = _run_events([{"type": "Ball Recovery", "location": [50, 40]}])
    assert stats["recoveries"] == 1


def test_defensive_event_mapping():
    stats = _run_events([
        {"type": "Pressure", "location": [50, 40]},
        {"type": "Interception", "location": [30, 40]},
        {"type": "Block", "location": [20, 40]},
        {"type": "Duel", "duel_type": "Tackle", "location": [25, 40]},
    ])
    assert stats["pressures"] == 1
    assert stats["interceptions"] == 1
    assert stats["blocks"] == 1
    assert stats["tackles"] == 1


def test_nan_xg_does_not_poison_total():
    # A present-but-NaN shot_statsbomb_xg must not turn the running sum into NaN.
    stats = _run_events([
        {"type": "Shot", "shot_statsbomb_xg": 0.3, "shot_outcome": "Goal", "location": [100, 40]},
        {"type": "Shot", "shot_statsbomb_xg": float("nan"), "shot_outcome": "Off T", "location": [100, 40]},
    ])
    assert stats["shots"] == 2
    assert stats["xg"] == pytest.approx(0.3)
    assert not np.isnan(stats["xg"])


def test_nan_assist_flags_not_counted():
    # Regression for the NaN-truthy bug: bool(NaN) is True, so the old row-loop
    # counted every pass with a NaN assist flag as an assist AND a key pass.
    stats = _run_events([
        {"type": "Pass", "pass_goal_assist": float("nan"), "pass_shot_assist": float("nan"), "location": [50, 40]},
        {"type": "Pass", "pass_goal_assist": float("nan"), "pass_shot_assist": float("nan"), "location": [50, 40]},
        {"type": "Pass", "pass_goal_assist": True, "pass_shot_assist": float("nan"), "location": [50, 40]},
        {"type": "Pass", "pass_goal_assist": float("nan"), "pass_shot_assist": True, "location": [50, 40]},
    ])
    assert stats["passes"] == 4
    assert stats["assists"] == 1          # only the real goal-assist
    assert stats["key_passes"] == 2       # one goal-assist + one shot-assist


def test_non_penalty_shot_counts():
    # np_shots / np_shots_on_target exclude penalties; raw shots include them.
    stats = _run_events([
        {"type": "Shot", "shot_type": "Penalty", "shot_outcome": "Goal", "shot_statsbomb_xg": 0.79, "location": [108, 40]},
        {"type": "Shot", "shot_type": "Open Play", "shot_outcome": "Saved", "shot_statsbomb_xg": 0.1, "location": [100, 40]},
        {"type": "Shot", "shot_type": "Open Play", "shot_outcome": "Off T", "shot_statsbomb_xg": 0.05, "location": [100, 40]},
    ])
    assert stats["shots"] == 3
    assert stats["shots_on_target"] == 2          # penalty goal + saved
    assert stats["np_shots"] == 2                 # penalty excluded
    assert stats["np_shots_on_target"] == 1       # only the saved open-play shot


def test_pass_geometry():
    # Final-third entry, penalty-area entry, and progressive pass thresholds.
    stats = _run_events([
        {"type": "Pass", "location": [70, 40], "pass_end_location": [90, 40]},    # f3 + prog
        {"type": "Pass", "location": [90, 40], "pass_end_location": [110, 40]},   # PA + prog
        {"type": "Pass", "location": [50, 40], "pass_end_location": [55, 40]},    # short, none
    ])
    assert stats["passes_f3"] == 1
    assert stats["passes_pa"] == 1
    assert stats["prog_passes"] == 2


def test_xg_per_shot_uses_non_penalty():
    data = {"minutes": [90], "np_xg": [0.6], "np_shots": [4], "passes": [10], "passes_completed": [8]}
    df = pd.DataFrame(data)
    out = calculate_scouting_metrics(df)
    assert out.iloc[0]["xg_per_shot"] == pytest.approx(0.15)


def test_schema_error_on_missing_event_column():
    from src.data_loader import _process_match_events, SchemaError
    bad = pd.DataFrame([{"type": "Pass"}])  # no player_id column
    agg = {1: {}}
    with patch("src.data_loader.sb.events", return_value=bad):
        with pytest.raises(SchemaError):
            _process_match_events("m1", agg, {1: []})


if __name__ == "__main__":
    # Simple manual run if pytest not desired
    test_calculate_scouting_metrics()
    test_normalize_metrics()
    test_scoring_logic()
    test_ball_recovery_increments_recoveries()
    test_defensive_event_mapping()
    test_nan_xg_does_not_poison_total()
    test_nan_assist_flags_not_counted()
    test_non_penalty_shot_counts()
    test_pass_geometry()
    test_xg_per_shot_uses_non_penalty()
    test_schema_error_on_missing_event_column()
    print("All core logic tests passed!")
