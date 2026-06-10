import plotly.express as px
import plotly.graph_objects as go
from mplsoccer import Pitch, VerticalPitch
import matplotlib.pyplot as plt
import pandas as pd

def plot_radar_chart(player_data, metrics):
    df = player_data[metrics].to_frame().reset_index()
    df.columns = ["metric", "value"]
    fig = px.line_polar(df, r="value", theta="metric", line_close=True)
    fig.update_traces(fill="toself")
    return fig

def plot_scatter_comparison(df, x_axis, y_axis):
    fig = px.scatter(df, x=x_axis, y=y_axis, hover_name="player", color="pos", size="minutes")
    return fig

def plot_spatial_heatmap(player_row, metric_prefix):
    vals = [
        player_row.get(f"{metric_prefix}_def", 0),
        player_row.get(f"{metric_prefix}_mid", 0),
        player_row.get(f"{metric_prefix}_final", 0)
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=[vals],
        x=['Defensive Third', 'Middle Third', 'Final Third'],
        y=['Zone'],
        colorscale='YlGnBu',
        showscale=False,
        text=[vals],
        texttemplate="%{text}"
    ))
    
    fig.update_layout(
        height=150,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(side="top"),
        yaxis=dict(visible=False)
    )
    return fig

def plot_activity_heatmap(event_list, action_type="All"):
    if not event_list:
        return None
    
    df = pd.DataFrame(event_list)
    
    if action_type == "Passes":
        df = df[df['type'] == 'Pass']
    elif action_type == "Shots":
        df = df[df['type'] == 'Shot']
    elif action_type == "Defensive":
        df = df[df['type'].isin(['Pressure', 'Interception', 'Ball Recovery', 'Block', 'Duel'])]
    elif action_type == "Carries":
        df = df[df['type'] == 'Carry']
    
    if df.empty:
        return None

    pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='#0e1117', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(8, 12))
    
    kde = pitch.kdeplot(df.x, df.y, ax=ax, fill=True, levels=100, thresh=0, cmap='hot', alpha=0.6)
    
    plt.tight_layout()
    return fig

def plot_historical_trend(history_df, metrics):
    fig = px.line(history_df, x="season_name", y=metrics, markers=True, 
                  title="Historical Performance Evolution")
    fig.update_layout(xaxis_title="Season", yaxis_title="Metric Value", legend_title="Metrics")
    return fig

