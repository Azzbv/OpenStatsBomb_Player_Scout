import pandas as pd
import numpy as np
from statsbombpy import sb
import streamlit as st

@st.cache_data
def get_competitions():
    return sb.competitions()

def _process_match_lineups(match_id, player_agg, player_events, player_id_filter=None):
    lineups = sb.lineups(match_id=match_id)
    for team, players_df in lineups.items():
        for p in players_df.to_dict('records'):
            p_id = p['player_id']
            if player_id_filter and p_id != player_id_filter:
                continue
                
            if p_id not in player_agg:
                player_agg[p_id] = {
                    "player": p['player_name'],
                    "team": team,
                    "minutes": 0, "matches": 0, "starts": 0, "pos_list": [],
                    "goals": 0, "np_goals": 0, "shots": 0, "shots_on_target": 0, 
                    "xg": 0.0, "np_xg": 0.0, "assists": 0, "key_passes": 0,
                    "passes": 0, "passes_completed": 0, "passes_f3": 0, "passes_pa": 0, "prog_passes": 0,
                    "carries": 0, "prog_carries": 0, "dribbles": 0, "dispossessions": 0, "miscontrols": 0,
                    "pressures": 0, "tackles": 0, "interceptions": 0, "recoveries": 0, "blocks": 0
                }
                player_events[p_id] = []
            
            player_agg[p_id]["matches"] += 1
            mins_in_match = 0
            for pos_entry in p['positions']:
                p_to = int(str(pos_entry['to']).split(':')[0]) if pos_entry['to'] is not None else 90
                p_from = int(str(pos_entry['from']).split(':')[0]) if pos_entry['from'] is not None else 0
                mins_in_match += (p_to - p_from)
                if pos_entry['start_reason'] == 'Starting XI':
                    player_agg[p_id]["starts"] += 1
                player_agg[p_id]["pos_list"].append(pos_entry['position'])
            player_agg[p_id]["minutes"] += mins_in_match

def _process_match_events(match_id, player_agg, player_events, player_id_filter=None):
    events = sb.events(match_id=match_id)
    for _, ev in events.iterrows():
        p_id = ev.get('player_id')
        if pd.isna(p_id) or p_id not in player_agg:
            continue
        if player_id_filter and p_id != player_id_filter:
            continue
            
        p_stats = player_agg[p_id]
        etype = ev['type']
        location = ev.get('location')
        
        if isinstance(location, list):
            player_events[p_id].append({'x': location[0], 'y': location[1], 'type': etype})
        
        sector = "Middle"
        if isinstance(location, list):
            x = location[0]
            if x < 40: sector = "Def"
            elif x > 80: sector = "Final"
        
        p_stats[f'actions_{sector}'] = p_stats.get(f'actions_{sector}', 0) + 1
        
        if etype == 'Shot':
            p_stats['shots'] += 1
            is_p = ev.get('shot_type') == 'Penalty'
            xg = ev.get('shot_statsbomb_xg', 0)
            p_stats['xg'] += xg
            if not is_p: p_stats['np_xg'] += xg
            if ev.get('shot_outcome') == 'Goal':
                p_stats['goals'] += 1
                if not is_p: p_stats['np_goals'] += 1
            if ev.get('shot_outcome') in ['Goal', 'Saved', 'Saved to Post']:
                p_stats['shots_on_target'] += 1
        elif etype == 'Pass':
            p_stats['passes'] += 1
            if pd.isna(ev.get('pass_outcome')): p_stats['passes_completed'] += 1
            if ev.get('pass_goal_assist'): p_stats['assists'] += 1
            if ev.get('pass_shot_assist') or ev.get('pass_goal_assist'):
                p_stats['key_passes'] += 1
            if isinstance(location, list) and isinstance(ev.get('pass_end_location'), list):
                sx, ex = location[0], ev['pass_end_location'][0]
                if sx < 80 and ex > 80: p_stats['passes_f3'] += 1
                if ex > 102 and 18 < ev['pass_end_location'][1] < 62 and sx < 102: p_stats['passes_pa'] += 1
                if ex > sx + 12: p_stats['prog_passes'] += 1
        elif etype == 'Carry':
            p_stats['carries'] += 1
            if isinstance(location, list) and isinstance(ev.get('carry_end_location'), list):
                if ev['carry_end_location'][0] > location[0] + 10: p_stats['prog_carries'] += 1
        elif etype == 'Dribble':
            if ev.get('dribble_outcome') == 'Complete': p_stats['dribbles'] += 1
        elif etype == 'Dispossessed': p_stats['dispossessions'] += 1
        elif etype == 'Miscontrol': p_stats['miscontrols'] += 1
        elif etype in ['Pressure', 'Interception', 'Ball Recovery', 'Block'] or (etype == 'Duel' and ev.get('duel_type') == 'Tackle'):
            key = 'pressures' if etype == 'Pressure' else etype.lower().replace(' ', '_') + 's' if etype != 'Duel' else 'tackles'
            p_stats[key] = p_stats.get(key, 0) + 1

def _compile_player_dataframe(player_agg):
    rows = []
    for p_id, s in player_agg.items():
        pos = max(set(s['pos_list']), key=s['pos_list'].count) if s['pos_list'] else "Unknown"
        for sec in ["Def", "Middle", "Final"]:
            for key in ["actions"]:
                if f"{key}_{sec}" not in s: s[f"{key}_{sec}"] = 0
        
        rows.append({
            "player_id": p_id, "player": s["player"], "team": s["team"], "pos": pos,
            "minutes": s["minutes"], "matches": s["matches"], "starts": s["starts"],
            "goals": s["goals"], "np_goals": s["np_goals"], "shots": s["shots"], "shots_on_target": s["shots_on_target"],
            "xg": s["xg"], "np_xg": s["np_xg"], "assists": s["assists"], "key_passes": s["key_passes"],
            "passes": s["passes"], "passes_completed": s["passes_completed"],
            "passes_f3": s["passes_f3"], "passes_pa": s["passes_pa"],
            "prog_passes": s["prog_passes"], "carries": s["carries"], "prog_carries": s["prog_carries"], "dribbles": s["dribbles"],
            "turnovers": s.get("dispossessions", 0) + s.get("miscontrols", 0),
            "tackles": s["tackles"], "interceptions": s["interceptions"], "pressures": s["pressures"],
            "recoveries": s["recoveries"], "blocks": s["blocks"],
            "actions_def": s.get("actions_Def", 0), "actions_mid": s.get("actions_Middle", 0), "actions_final": s.get("actions_Final", 0),
            "final_third_ratio": s.get("actions_Final", 0) / max(1, (s.get("actions_Def", 0) + s.get("actions_Middle", 0) + s.get("actions_Final", 0))),
            "age": None, "market_value": None, "league": "StatsBomb", "season": "Open", "foot": "Unknown"
        })
    return pd.DataFrame(rows)

@st.cache_data
def load_statsbomb_player_data(competition_id, season_id, max_matches=10):
    matches = sb.matches(competition_id=competition_id, season_id=season_id)
    match_subset = matches.head(max_matches)["match_id"].tolist()
    player_agg, player_events = {}, {}
    for m_id in match_subset: _process_match_lineups(m_id, player_agg, player_events)
    for m_id in match_subset: _process_match_events(m_id, player_agg, player_events)
    return _compile_player_dataframe(player_agg), player_events

@st.cache_data
def load_multiple_competitions(comp_season_pairs, max_matches_per_comp=5):
    player_agg, player_events = {}, {}
    for c_id, s_id in comp_season_pairs:
        matches = sb.matches(competition_id=c_id, season_id=s_id)
        match_subset = matches.head(max_matches_per_comp)["match_id"].tolist()
        for m_id in match_subset: _process_match_lineups(m_id, player_agg, player_events)
        for m_id in match_subset: _process_match_events(m_id, player_agg, player_events)
    return _compile_player_dataframe(player_agg), player_events

@st.cache_data
def fetch_player_history(player_id, competition_id, max_matches_per_season=10):
    comps = sb.competitions()
    seasons = comps[comps["competition_id"] == competition_id].sort_values("season_name")
    
    history_rows = []
    for _, s_row in seasons.iterrows():
        p_agg, p_ev = {}, {}
        matches = sb.matches(competition_id=competition_id, season_id=s_row["season_id"])
        match_subset = matches.head(max_matches_per_season)["match_id"].tolist()
        for m_id in match_subset: _process_match_lineups(m_id, p_agg, p_ev, player_id_filter=player_id)
        if player_id in p_agg:
            for m_id in match_subset: _process_match_events(m_id, p_agg, p_ev, player_id_filter=player_id)
            df_season = _compile_player_dataframe(p_agg)
            if not df_season.empty:
                row = df_season.iloc[0].to_dict()
                row["season_name"] = s_row["season_name"]
                history_rows.append(row)
    return pd.DataFrame(history_rows)

def clean_player_data(df):
    df = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns
    df[categorical_cols] = df[categorical_cols].fillna("Unknown")
    return df
