import plotly.express as px
import plotly.graph_objects as go
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt
import pandas as pd

# Chart tokens (mirror src/style.py; keep in sync).
COLOR_HOME = "#2563eb"   # primary series (== ACCENT)
COLOR_AWAY = "#475569"   # secondary series
PITCH_LINE = "#dfe5ee"   # pitch markings (hairline)
PITCH_BG = "none"        # transparent pitch background
PLOT_FONT = "#64748b"    # muted chart labels (== MUTED)
BODY = "#334155"         # chart body copy
GRID = "#eef2f7"         # plotly / polar grid lines

FONT_FAMILY = (
    "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
    "Helvetica, Arial, sans-serif"
)


def _pitch(figsize=(8, 12)):
    """Return ``(pitch, fig, ax)`` with a transparent figure + axes and
    ``PITCH_LINE`` markings. Never instantiate ``VerticalPitch`` directly;
    route through here so every pitch matches."""
    pitch = VerticalPitch(
        pitch_type="statsbomb", pitch_color=PITCH_BG, line_color=PITCH_LINE,
        linewidth=1,
    )
    fig, ax = pitch.draw(figsize=figsize)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    return pitch, fig, ax


def _style_plotly(fig, height=None):
    """Apply the shared plotly chrome: transparent background, Inter font,
    slim margins, faint y-grid, top-left horizontal legend. Call after building
    the figure, then layer per-chart tweaks on the next line."""
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT_FAMILY, color=BODY, size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=28, b=8),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            title_text="",
        ),
    )
    fig.update_xaxes(showgrid=False, color=PLOT_FONT)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, color=PLOT_FONT)
    if height is not None:
        fig.update_layout(height=height)
    return fig


def plot_radar_chart(player_data, metrics):
    df = player_data[metrics].to_frame().reset_index()
    df.columns = ["metric", "value"]
    fig = px.line_polar(df, r="value", theta="metric", line_close=True)
    fig.update_traces(
        fill="toself",
        line_color=COLOR_HOME,
        fillcolor="rgba(37, 99, 235, 0.12)",
    )
    fig.update_layout(
        template="plotly_white",
        font=dict(family=FONT_FAMILY, color=BODY, size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=28, b=28),
        height=360,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(gridcolor=GRID, linecolor=GRID, tickfont=dict(color=PLOT_FONT)),
            angularaxis=dict(gridcolor=GRID, linecolor=GRID, tickfont=dict(color=PLOT_FONT)),
        ),
    )
    return fig


def plot_scatter_comparison(df, x_axis, y_axis):
    fig = px.scatter(
        df, x=x_axis, y=y_axis, hover_name="player", color="pos",
        size="minutes",
    )
    _style_plotly(fig, height=420)
    fig.update_layout(legend_title_text="")
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
        colorscale='Blues',
        showscale=False,
        text=[vals],
        texttemplate="%{text}",
        textfont=dict(color=BODY),
    ))

    _style_plotly(fig, height=150)
    fig.update_layout(margin=dict(l=8, r=8, t=20, b=8))
    fig.update_xaxes(side="top")
    fig.update_yaxes(visible=False)
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

    pitch, fig, ax = _pitch(figsize=(8, 12))
    pitch.kdeplot(df.x, df.y, ax=ax, fill=True, levels=100, thresh=0, cmap='Blues', alpha=0.75)

    plt.tight_layout()
    return fig


def plot_historical_trend(history_df, metrics):
    fig = px.line(
        history_df, x="season_name", y=metrics, markers=True,
        color_discrete_sequence=[COLOR_HOME, COLOR_AWAY, "#94a3b8", "#0f172a", "#3b82f6"],
    )
    _style_plotly(fig, height=360)
    fig.update_layout(
        xaxis_title="Season", yaxis_title="Metric Value", legend_title_text="",
    )
    return fig
