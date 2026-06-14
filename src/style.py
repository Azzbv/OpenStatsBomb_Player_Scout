"""Visual design system for the Player Scout dashboard.

Source of truth for the HTML/CSS chrome. Color tokens defined here are mirrored
in ``src/visuals.py`` for charts; keep the two in sync (see STYLEGUIDE.md).
Never hardcode these hex values at a call site; reference the token.
"""

import html

# Color tokens.
ACCENT = "#2563eb"       # Primary accent; selected states
ACCENT_SOFT = "#eff4ff"  # Tint for hover/selected fills (reserved)
INK = "#0f172a"          # Primary text, headings
MUTED = "#64748b"        # Secondary text, labels, captions
HAIRLINE = "#e9edf3"     # All borders, dividers, table rules
SURFACE = "#ffffff"      # Cards, sidebar, metrics, chips
CANVAS = "#fbfcfe"       # App background, table header fill
BODY = "#334155"         # Body copy (one step above MUTED)

FONT_STACK = (
    "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
    "Helvetica, Arial, sans-serif"
)


def apply_custom_style():
    """Inject the global CSS. Call once, right after ``st.set_page_config``."""
    import streamlit as st

    st.markdown(
        f"""
        <style>
        /* ---- Base ---------------------------------------------------- */
        html, body, [class*="css"] {{
            font-family: {FONT_STACK};
        }}
        .stApp {{
            background: {CANVAS};
            color: {INK};
        }}
        .block-container {{
            padding-top: 2.2rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }}

        /* ---- Headings ------------------------------------------------ */
        h1, h2, h3 {{
            color: {INK};
            font-weight: 650;
            letter-spacing: -0.015em;
        }}
        h4, h5, h6 {{
            color: {INK};
            font-weight: 600;
            letter-spacing: -0.01em;
        }}
        /* Section labels (#### …) render as small uppercase captions */
        h4 {{
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.09em;
            text-transform: uppercase;
            color: {MUTED};
        }}

        /* ---- Sidebar ------------------------------------------------- */
        [data-testid="stSidebar"] {{
            background: {SURFACE};
            border-right: 1px solid {HAIRLINE};
        }}
        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 1.4rem;
        }}

        /* ---- Dividers ------------------------------------------------ */
        hr {{
            border: none;
            border-top: 1px solid {HAIRLINE};
            margin: 1rem 0;
        }}

        /* ---- Captions ------------------------------------------------ */
        [data-testid="stCaptionContainer"] {{
            color: {MUTED};
        }}

        /* ---- Metrics ------------------------------------------------- */
        [data-testid="stMetric"] {{
            background: {SURFACE};
            border: 1px solid {HAIRLINE};
            border-radius: 10px;
            padding: 0.8rem 1rem;
        }}
        [data-testid="stMetricLabel"] p {{
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: {MUTED};
        }}
        [data-testid="stMetricValue"] {{
            font-size: 1.6rem;
            font-weight: 650;
            letter-spacing: -0.02em;
            color: {INK};
            font-variant-numeric: tabular-nums;
        }}

        /* ---- Tabs ---------------------------------------------------- */
        [data-baseweb="tab-list"] {{
            background: transparent;
            border-bottom: 1px solid {HAIRLINE};
            gap: 1.4rem;
        }}
        [data-baseweb="tab"] {{
            background: transparent !important;
            padding: 0.4rem 0 !important;
        }}
        [data-baseweb="tab"] p {{
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {MUTED};
        }}
        [data-baseweb="tab"][aria-selected="true"] p {{
            color: {ACCENT};
        }}
        [data-baseweb="tab-highlight"] {{
            background: {ACCENT} !important;
            height: 2px !important;
        }}

        /* ---- Tables / dataframes ------------------------------------- */
        [data-testid="stTable"] table, .stDataFrame {{
            font-variant-numeric: tabular-nums;
            font-size: 0.84rem;
            border-radius: 8px;
            overflow: hidden;
        }}
        [data-testid="stTable"] thead th {{
            background: {CANVAS} !important;
            font-size: 0.72rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.05em !important;
            text-transform: uppercase !important;
            color: {MUTED} !important;
            border-bottom: 1px solid {HAIRLINE} !important;
        }}
        [data-testid="stTable"] tbody td {{
            border-bottom: 1px solid {HAIRLINE} !important;
        }}

        /* ---- Inputs -------------------------------------------------- */
        [data-testid="stWidgetLabel"] p, .stSelectbox label, .stRadio label {{
            font-size: 0.78rem;
            font-weight: 600;
            color: {MUTED};
        }}
        [data-baseweb="select"] > div, .stTextInput input,
        .stNumberInput input {{
            border-radius: 8px;
            border-color: {HAIRLINE};
            font-size: 0.86rem;
        }}

        /* ---- Insight chips ------------------------------------------- */
        .insight-item {{
            background: {SURFACE};
            border: 1px solid {HAIRLINE};
            border-left: 2px solid {ACCENT};
            border-radius: 7px;
            padding: 0.6rem 0.85rem;
            margin-bottom: 0.5rem;
            font-size: 0.86rem;
            color: {BODY};
        }}
        .insight-item b {{ color: {INK}; }}

        /* ---- Hidden chrome ------------------------------------------- */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        [data-testid="stDecoration"] {{ display: none; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def safe(text):
    """HTML-escape an arbitrary (possibly data-derived) string for safe rendering.

    Streamlit renders inline HTML inside markdown sinks, so any string that
    originates from external data (player names, team names, free text) must be
    escaped before it reaches ``st.markdown``/``st.success``/``st.info`` etc.
    """
    return html.escape(str(text))


def format_insight(text):
    """HTML-escape ``text`` then re-introduce ``**bold**`` as ``<b>``.

    Returns an ``.insight-item`` chip with a leading bullet. Any data-derived
    string must pass through here (or be escaped) before rendering with
    ``unsafe_allow_html=True``.
    """
    escaped = html.escape(text)
    while "**" in escaped:
        escaped = escaped.replace("**", "<b>", 1)
        escaped = escaped.replace("**", "</b>", 1)
    return f'<div class="insight-item">• {escaped}</div>'
