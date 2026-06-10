import streamlit as st
import pandas as pd
from src.data_loader import get_competitions, load_statsbomb_player_data, clean_player_data, load_multiple_competitions, fetch_player_history
from src.transforms import filter_players, normalize_metrics, map_positions_to_roles, filter_by_minutes, filter_by_matches
from src.metrics import calculate_scouting_metrics, get_metric_categories
from src.scoring import calculate_recruitment_score, get_role_templates, get_fit_breakdown
from src.visuals import plot_radar_chart, plot_scatter_comparison, plot_spatial_heatmap, plot_activity_heatmap, plot_historical_trend
from src.insights import get_top_traits, generate_recruitment_report, generate_tldr_summary
from src.comparison import get_best_in_categories, generate_scouting_note
from src.glossary import get_metric_glossary

st.set_page_config(page_title="ScoutDash | StatsBomb", layout="wide")

def main():
    st.title("⚽ Player Recruitment Dashboard (StatsBomb Open Data)")
    
    st.sidebar.header("Data Source")
    comps_df = get_competitions()
    
    global_scope = st.sidebar.checkbox("🌍 Enable Global Scope", help="Aggregate data across multiple leagues in the same year/gender.")
    
    sample_limit = st.sidebar.slider("Match Sample Limit", 1, 38, 5, help="Number of matches to scan per league.")
    st.sidebar.warning("⚠️ Data is sampled for performance.")
    
    if global_scope:
        genders = sorted(list(comps_df["competition_gender"].unique()))
        sel_gender = st.sidebar.selectbox("Gender", genders)
        
        years = sorted(list(comps_df["season_name"].unique()), reverse=True)
        sel_year = st.sidebar.selectbox("Season Year", years)
        
        matching_comps = comps_df[
            (comps_df["competition_gender"] == sel_gender) & 
            (comps_df["season_name"] == sel_year)
        ]
        
        if matching_comps.empty:
            st.sidebar.error("No competitions found for this year/gender.")
            return
            
        comp_pairs = list(zip(matching_comps["competition_id"], matching_comps["season_id"]))
        
        tracked_leagues = sorted(list(matching_comps["competition_name"].unique()))
        st.sidebar.info(f"Tracking {len(comp_pairs)} competitions.")
        with st.sidebar.expander("View Tracked Leagues"):
            for league in tracked_leagues:
                st.write(f"- {league}")
        
        with st.spinner("Processing Global StatsBomb data..."):
            raw_df, all_player_events = load_multiple_competitions(comp_pairs, max_matches_per_comp=sample_limit)
        
        ref_comp_id = matching_comps.iloc[0]["competition_id"]
        sel_comp = "Global Scope"
        sel_season = sel_year
        
    else:
        comp_names = sorted(list(comps_df["competition_name"].unique()))
        sel_comp = st.sidebar.selectbox("Competition", comp_names)
        
        seasons_df = comps_df[comps_df["competition_name"] == sel_comp]
        sel_season = st.sidebar.selectbox("Season", seasons_df["season_name"].unique())
        
        comp_row = seasons_df[seasons_df["season_name"] == sel_season].iloc[0]
        ref_comp_id = comp_row["competition_id"]
        
        with st.spinner("Processing StatsBomb events..."):
            raw_df, all_player_events = load_statsbomb_player_data(comp_row["competition_id"], comp_row["season_id"], max_matches=sample_limit)
        
    df = clean_player_data(raw_df)
    df = map_positions_to_roles(df)
    df = calculate_scouting_metrics(df)
    
    st.sidebar.markdown("---")
    st.sidebar.header("Global Filters")
    
    teams = ["All"] + sorted(list(df["team"].unique()))
    sel_team = st.sidebar.selectbox("Filter Team", teams)
    
    col_f1, col_f2 = st.sidebar.columns(2)
    with col_f1:
        min_mins = st.number_input("Min Minutes", 0, 3800, 90)
    with col_f2:
        min_matches = st.number_input("Min Matches", 0, 38, 1)
    
    roles = ["All"] + sorted(list(df["role_group"].unique()))
    sel_role_group = st.sidebar.selectbox("Role Group", roles)
    
    f_df = df.copy()
    if sel_team != "All": f_df = f_df[f_df["team"] == sel_team]
    f_df = filter_by_minutes(f_df, min_mins)
    f_df = filter_by_matches(f_df, min_matches)
    f_df = filter_players(f_df, role_group=None if sel_role_group == "All" else sel_role_group)

    st.sidebar.markdown("---")
    st.sidebar.header("Scouting Profile")
    templates = get_role_templates()
    use_template = st.sidebar.checkbox("Use Role Template", value=True)
    
    all_metrics = []
    default_weights = {}
    
    if use_template:
        template_name = st.sidebar.selectbox("Select Role Template", list(templates.keys()))
        default_weights = templates[template_name]
        all_metrics = list(default_weights.keys())
    else:
        categories = get_metric_categories()
        for cat, ms in categories.items():
            available = [m for m in ms if m in f_df.columns]
            if available:
                with st.sidebar.expander(f"{cat} Metrics"):
                    selected = st.multiselect(f"Select {cat}", available)
                    all_metrics.extend(selected)

    st.sidebar.markdown("---")
    with st.sidebar.expander("📖 Metric Glossary"):
        glossary = get_metric_glossary()
        for k, info in glossary.items():
            if k in ["xg", "key_passes", "prog_passes", "pressures", "turnovers", "scout_score"]:
                st.markdown(f"**{info['display']}**")
                st.caption(info['definition'])
                st.markdown(f"*Why it matters:* {info['rationale']}")
                st.divider()

    if not all_metrics:
        st.warning("Please select a profile in the sidebar.")
        return

    valid_metrics = [m for m in all_metrics if m in f_df.columns]
    df_norm = normalize_metrics(f_df, valid_metrics)
    
    weights = {m: st.sidebar.slider(m.replace('_', ' ').title(), -10, 10, default_weights.get(m, 5)) for m in valid_metrics}
    scored_df = calculate_recruitment_score(df_norm, weights)
    scored_df = scored_df.sort_values("scout_score", ascending=False)

    tabs = st.tabs(["📊 Ranking", "⚖️ Comparison", "👤 Player Profile", "📖 Metric Guide"])

    with tabs[0]:
        st.subheader(f"Top Targets: {sel_comp} ({sel_season})", help="Ranked by Fit Score.")
        display_cols = ["player", "team", "pos", "role_group", "minutes", "matches", "scout_score"]
        st.dataframe(
            scored_df[display_cols].head(25).style.format({"scout_score": "{:.1f}"})
                                              .background_gradient(subset=["scout_score"], cmap="YlGn"),
            use_container_width=True
        )
        
        st.subheader("Tactical Distribution")
        cx, cy = st.columns(2)
        with cx: x_ax = st.selectbox("X-Axis", valid_metrics, index=0)
        with cy: y_ax = st.selectbox("Y-Axis", valid_metrics, index=min(1, len(valid_metrics)-1))
        st.plotly_chart(plot_scatter_comparison(scored_df, x_ax, y_ax), use_container_width=True, key="main_scatter")

    with tabs[1]:
        st.subheader("Player Comparison")
        comp_players = st.multiselect("Select players (2-5)", scored_df["player"].tolist(), default=scored_df["player"].head(2).tolist())
        
        if len(comp_players) >= 2:
            comp_df = scored_df[scored_df["player"].isin(comp_players)]
            
            leaders = get_best_in_categories(comp_df, get_metric_categories())
            st.markdown("### Category Leaders")
            cols = st.columns(len(leaders))
            for i, (cat, leader) in enumerate(leaders.items()):
                with cols[i]: st.success(f"**{cat}**\n\n{leader}")

            st.markdown("---")
            r_cols = st.columns(len(comp_players))
            for i, p_name in enumerate(comp_players):
                p_row = comp_df[comp_df["player"] == p_name].iloc[0]
                with r_cols[i]:
                    st.markdown(f"**{p_name}**")
                    st.plotly_chart(plot_radar_chart(p_row, [f"{m}_norm" for m in valid_metrics]), use_container_width=True, key=f"comp_{p_name}")
                    st.write(generate_scouting_note(p_row, weights, get_metric_categories()))
        else:
            st.info("Select 2+ players for comparison.")

    with tabs[2]:
        st.subheader("Detailed Scouting Profile")
        sel_p = st.selectbox("Search Player", scored_df["player"].tolist())
        p_row = scored_df[scored_df["player"] == sel_p].iloc[0]
        p_id = p_row["player_id"]
        
        tldr = generate_tldr_summary(p_row, get_metric_categories())
        with st.container():
            st.markdown(f"#### ⚡ TL;DR: {sel_p}")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown(f"**Profile:** {tldr['profile']}")
                st.markdown(f"**Advantages:** {tldr['advantages']}")
            with col_t2:
                st.markdown(f"**Weaknesses:** {tldr['weaknesses']}")
                st.markdown(f"**Fit:** {tldr['fit']}")
        st.markdown("---")

        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            st.metric("Fit Score", f"{p_row['scout_score']:.1f}", help=glossary['scout_score']['definition'])
            st.markdown(f"**Team:** {p_row['team']}\n\n**Matches:** {p_row['matches']} ({int(p_row['minutes'])} mins)")
        with c2:
            st.markdown(f"**Position:** {p_row['pos']}\n\n**Role:** {p_row['role_group']}")
        with c3:
            st.plotly_chart(plot_radar_chart(p_row, [f"{m}_norm" for m in valid_metrics]), use_container_width=True, key="prof_radar")
            
        st.markdown("---")
        st.markdown("### 📍 Pitch Activity Heatmap")
        st.caption("Visualizing event start locations (Gaussian KDE).")
        
        h1, h2 = st.columns([2, 1])
        with h2:
            act_type = st.radio("Visualize Activity:", ["All Actions", "Passes", "Carries", "Defensive", "Shots"])
            
            st.markdown("**Zone Involvement:**")
            st.write(f"- Defensive Third: {p_row['actions_def']:.0f} actions")
            st.write(f"- Middle Third: {p_row['actions_mid']:.0f} actions")
            st.write(f"- Final Third: {p_row['actions_final']:.0f} actions ({p_row['final_third_ratio']*100:.1f}%)")

        with h1:
            events = all_player_events.get(p_id, [])
            fig = plot_activity_heatmap(events, action_type=act_type.split()[0])
            if fig:
                st.pyplot(fig)
                import matplotlib.pyplot as plt
                plt.close(fig)
            else:
                st.warning("No spatial data found for selected activity type.")

        st.markdown("---")
        st.markdown("### Spatial Intensity (Sector Aggregate)")
        s1, s2, s3 = st.columns(3)
        with s1:
            st.caption("Total Actions by Third")
            st.plotly_chart(plot_spatial_heatmap(p_row, "actions"), use_container_width=True, key="spat_act")
        with s2:
            st.caption("Defensive Actions by Third")
            st.plotly_chart(plot_spatial_heatmap(p_row, "def"), use_container_width=True, key="spat_def")
        with s3:
            st.caption("Progression Actions by Third")
            st.plotly_chart(plot_spatial_heatmap(p_row, "prog"), use_container_width=True, key="spat_prog")

        st.markdown("---")
        report = generate_recruitment_report(p_row, get_metric_categories(), valid_metrics)
        st.markdown(f"### Recruitment Insight: {sel_p}")
        st.info(f"**Summary:** {report['summary']}")
        
        b1, b2 = st.columns(2)
        with b1:
            st.success("**Strengths**")
            for s in report["strengths"]: st.write(f"✅ {s}")
            st.markdown("**Role Fit**")
            st.write(report["role_fit"])
        with b2:
            st.warning("**Risks**")
            for r in report["risks"]: st.write(f"⚠️ {r}")
            st.markdown("**Recommendation**")
            st.write(report["recommendation"])
            
        st.markdown("---")
        st.markdown("### ⏳ Time Machine: Historical Trend")
        st.caption("Track performance evolution across past seasons.")
        
        if st.button(f"Load History for {sel_p}"):
            with st.spinner(f"Fetching history..."):
                hist_df = fetch_player_history(p_id, ref_comp_id)
                
                if not hist_df.empty:
                    hist_df = calculate_scouting_metrics(hist_df)
                    
                    final_plot_metrics = []
                    for m in ["goals", "xg", "key_passes", "prog_passes", "tackles"]:
                        col = f"{m}_per90"
                        if col in hist_df.columns: final_plot_metrics.append(col)
                    
                    st.plotly_chart(plot_historical_trend(hist_df, final_plot_metrics), use_container_width=True)
                    
                    st.markdown("**Season Breakdown:**")
                    st.dataframe(hist_df[["season_name", "team", "matches", "minutes"] + final_plot_metrics].set_index("season_name"), use_container_width=True)
                else:
                    st.warning("No historical seasons found.")

    with tabs[3]:
        st.subheader("📖 Metric Guide & Methodology")
        
        glossary = get_metric_glossary()
        cats = sorted(list(set(info["category"] for info in glossary.values())))
        search = st.text_input("🔍 Search metrics...", placeholder="e.g. xG")
        
        for cat in cats:
            st.markdown(f"### {cat}")
            cat_metrics = {k: v for k, v in glossary.items() if v["category"] == cat}
            for k, info in cat_metrics.items():
                if search.lower() in info["display"].lower() or search.lower() in info["definition"].lower():
                    with st.expander(f"{info['display']} ({info['note']})"):
                        st.markdown(f"**Definition:** {info['definition']}")
                        st.markdown(f"**Tactical Rationale:** {info['rationale']}")
                        st.markdown(f"**Calculation:** `{info['method']}`")

if __name__ == "__main__":
    main()
