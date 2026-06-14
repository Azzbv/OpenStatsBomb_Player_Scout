import pandas as pd
import numpy as np
from statsbombpy import sb
import streamlit as st


class SchemaError(RuntimeError):
    """Raised when a StatsBomb payload is missing columns we depend on.

    statsbombpy omits *optional* event columns when no event in a match used
    them (handled gracefully by ``_col``), but the columns below are essential:
    without them aggregation is meaningless. Validating in one place turns a
    schema drift into a single clear error instead of scattered KeyErrors.
    """


# Minimal columns each frame must contain for aggregation to be meaningful.
_REQUIRED_EVENT_COLS = {"type", "player_id"}
_REQUIRED_LINEUP_COLS = {"player_id", "player_name", "positions"}


def _require_columns(frame, required, source):
    missing = required - set(frame.columns)
    if missing:
        raise SchemaError(
            f"StatsBomb {source} payload is missing required column(s): "
            f"{sorted(missing)}. The upstream schema may have changed."
        )


@st.cache_data
def get_competitions():
    return sb.competitions()

def _process_match_lineups(match_id, player_agg, player_events, player_id_filter=None):
    lineups = sb.lineups(match_id=match_id)
    for team, players_df in lineups.items():
        _require_columns(players_df, _REQUIRED_LINEUP_COLS, "lineups")
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
                    "np_shots": 0, "np_shots_on_target": 0,
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

_DEFENSIVE_KEY = {
    'Pressure': 'pressures',
    'Interception': 'interceptions',
    'Ball Recovery': 'recoveries',
    'Block': 'blocks',
}


def _col(events, name):
    """Return a column as a Series, or an all-NaN Series if the column is absent.
    statsbombpy omits columns entirely when no event in the match used them."""
    if name in events.columns:
        return events[name]
    return pd.Series([np.nan] * len(events), index=events.index)


def _list_coord(series, idx):
    """Vectorized extraction of element `idx` from list-valued cells (e.g.
    location -> x/y). Non-list cells (NaN) yield NaN."""
    return series.map(lambda v: v[idx] if isinstance(v, list) else np.nan)


def _process_match_events(match_id, player_agg, player_events, player_id_filter=None):
    events = sb.events(match_id=match_id)
    if events.empty:
        return
    _require_columns(events, _REQUIRED_EVENT_COLS, "events")

    pid = pd.to_numeric(_col(events, 'player_id'), errors='coerce')
    tracked = set(player_agg.keys())
    if player_id_filter is not None:
        tracked = tracked & {player_id_filter}
    mask = pid.notna() & pid.isin(tracked)
    if not mask.any():
        return
    ev = events.loc[mask].copy()
    ev['_pid'] = pid.loc[mask]

    etype = _col(ev, 'type')
    loc = _col(ev, 'location')
    x = _list_coord(loc, 0)
    has_loc = loc.map(lambda v: isinstance(v, list))

    # Per-event location records for the KDE heatmap, in original order.
    loc_rows = ev.loc[has_loc.values]
    if not loc_rows.empty:
        rec = pd.DataFrame({
            '_pid': loc_rows['_pid'].values,
            'x': _list_coord(_col(loc_rows, 'location'), 0).values,
            'y': _list_coord(_col(loc_rows, 'location'), 1).values,
            'type': _col(loc_rows, 'type').values,
        })
        for p_id, grp in rec.groupby('_pid', sort=False):
            player_events[p_id].extend(
                grp[['x', 'y', 'type']].to_dict('records')
            )

    sector = pd.Series('Middle', index=ev.index)
    sector[x < 40] = 'Def'
    sector[x > 80] = 'Final'
    _add_counts(player_agg, ev['_pid'], sector.map(
        {'Def': 'actions_Def', 'Middle': 'actions_Middle', 'Final': 'actions_Final'}
    ))

    is_shot = etype == 'Shot'
    shot_type = _col(ev, 'shot_type')
    is_pen = shot_type == 'Penalty'
    outcome = _col(ev, 'shot_outcome')
    # NaN xG must not poison sums; coerce to 0.0 (a missing value is no xG).
    xg = pd.to_numeric(_col(ev, 'shot_statsbomb_xg'), errors='coerce').fillna(0.0)

    _add_counts(player_agg, ev['_pid'], is_shot, 'shots')
    _add_sums(player_agg, ev['_pid'], xg.where(is_shot, 0.0), 'xg')
    _add_sums(player_agg, ev['_pid'], xg.where(is_shot & ~is_pen, 0.0), 'np_xg')
    is_goal = is_shot & (outcome == 'Goal')
    _add_counts(player_agg, ev['_pid'], is_goal, 'goals')
    _add_counts(player_agg, ev['_pid'], is_goal & ~is_pen, 'np_goals')
    _add_counts(player_agg, ev['_pid'],
                is_shot & outcome.isin(['Goal', 'Saved', 'Saved to Post']),
                'shots_on_target')
    # Non-penalty shot volume keeps shot metrics consistent with np_xg.
    _add_counts(player_agg, ev['_pid'], is_shot & ~is_pen, 'np_shots')
    _add_counts(player_agg, ev['_pid'],
                is_shot & ~is_pen & outcome.isin(['Goal', 'Saved', 'Saved to Post']),
                'np_shots_on_target')

    is_pass = etype == 'Pass'
    pass_outcome = _col(ev, 'pass_outcome')
    completed = is_pass & pass_outcome.isna()  # completed passes have a NaN outcome
    # Compare with `== True`, not plain truthiness: bool(NaN) is True, which would
    # count every NaN-flagged pass as an assist/key pass.
    goal_assist = _col(ev, 'pass_goal_assist') == True  # noqa: E712
    shot_assist = _col(ev, 'pass_shot_assist') == True  # noqa: E712
    _add_counts(player_agg, ev['_pid'], is_pass, 'passes')
    _add_counts(player_agg, ev['_pid'], completed, 'passes_completed')
    _add_counts(player_agg, ev['_pid'], is_pass & goal_assist, 'assists')
    _add_counts(player_agg, ev['_pid'], is_pass & (shot_assist | goal_assist), 'key_passes')

    pass_end = _col(ev, 'pass_end_location')
    has_pass_end = pass_end.map(lambda v: isinstance(v, list))
    ex = _list_coord(pass_end, 0)
    ey = _list_coord(pass_end, 1)
    pass_geo = is_pass & has_loc & has_pass_end
    _add_counts(player_agg, ev['_pid'], pass_geo & (x < 80) & (ex > 80), 'passes_f3')
    _add_counts(player_agg, ev['_pid'],
                pass_geo & (ex > 102) & (ey > 18) & (ey < 62) & (x < 102), 'passes_pa')
    _add_counts(player_agg, ev['_pid'], pass_geo & (ex > x + 12), 'prog_passes')

    is_carry = etype == 'Carry'
    carry_end = _col(ev, 'carry_end_location')
    has_carry_end = carry_end.map(lambda v: isinstance(v, list))
    cex = _list_coord(carry_end, 0)
    _add_counts(player_agg, ev['_pid'], is_carry, 'carries')
    _add_counts(player_agg, ev['_pid'],
                is_carry & has_loc & has_carry_end & (cex > x + 10), 'prog_carries')

    _add_counts(player_agg, ev['_pid'],
                (etype == 'Dribble') & (_col(ev, 'dribble_outcome') == 'Complete'),
                'dribbles')
    _add_counts(player_agg, ev['_pid'], etype == 'Dispossessed', 'dispossessions')
    _add_counts(player_agg, ev['_pid'], etype == 'Miscontrol', 'miscontrols')

    for sb_type, out_key in _DEFENSIVE_KEY.items():
        _add_counts(player_agg, ev['_pid'], etype == sb_type, out_key)
    is_tackle = (etype == 'Duel') & (_col(ev, 'duel_type') == 'Tackle')
    _add_counts(player_agg, ev['_pid'], is_tackle, 'tackles')


def _add_counts(player_agg, pids, mask_or_keys, key=None):
    """Increment `key` by the per-player count of True rows in `mask_or_keys`,
    or, when `key` is None, treat `mask_or_keys` as a Series of target keys
    (one per row) and increment each."""
    if key is None:
        keys = mask_or_keys
        for p_id, grp in keys.groupby(pids, sort=False):
            for out_key, n in grp.value_counts().items():
                player_agg[p_id][out_key] = player_agg[p_id].get(out_key, 0) + int(n)
        return
    mask = mask_or_keys.fillna(False).astype(bool)
    if not mask.any():
        return
    counts = pids[mask.values].value_counts()
    for p_id, n in counts.items():
        player_agg[p_id][key] = player_agg[p_id].get(key, 0) + int(n)


def _add_sums(player_agg, pids, values, key):
    """Add the per-player sum of `values` into `key`."""
    sums = values.groupby(pids, sort=False).sum()
    for p_id, total in sums.items():
        if total:
            player_agg[p_id][key] = player_agg[p_id].get(key, 0.0) + float(total)

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
            "np_shots": s.get("np_shots", 0), "np_shots_on_target": s.get("np_shots_on_target", 0),
            "xg": s["xg"], "np_xg": s["np_xg"], "assists": s["assists"], "key_passes": s["key_passes"],
            "passes": s["passes"], "passes_completed": s["passes_completed"],
            "passes_f3": s["passes_f3"], "passes_pa": s["passes_pa"],
            "prog_passes": s["prog_passes"], "carries": s["carries"], "prog_carries": s["prog_carries"], "dribbles": s["dribbles"],
            "turnovers": s.get("dispossessions", 0) + s.get("miscontrols", 0),
            "tackles": s["tackles"], "interceptions": s["interceptions"], "pressures": s["pressures"],
            "recoveries": s["recoveries"], "blocks": s["blocks"],
            "actions_def": s.get("actions_Def", 0), "actions_mid": s.get("actions_Middle", 0), "actions_final": s.get("actions_Final", 0),
            "final_third_ratio": s.get("actions_Final", 0) / max(1, (s.get("actions_Def", 0) + s.get("actions_Middle", 0) + s.get("actions_Final", 0))),
            # age / market value / preferred foot are not in StatsBomb Open Data
            # and are intentionally omitted; do not re-add them as placeholders.
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
