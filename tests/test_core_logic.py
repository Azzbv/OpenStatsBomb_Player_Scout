import pandas as pd
import numpy as np
import pytest
from src.metrics import calculate_scouting_metrics
from src.scoring import calculate_recruitment_score, get_role_templates
from src.transforms import normalize_metrics

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
    
    assert df_norm["val_norm"].min() == 0.0
    assert df_norm["val_norm"].max() == 1.0
    assert df_norm["val_norm"].iloc[1] == 0.5

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

if __name__ == "__main__":
    # Simple manual run if pytest not desired
    test_calculate_scouting_metrics()
    test_normalize_metrics()
    test_scoring_logic()
    print("All core logic tests passed!")
