# ScoutDash: Advanced Recruitment Analytics

A player recruitment dashboard built with Python, Streamlit, and StatsBomb Open
Data. ScoutDash transforms raw event-level data into tactical fit rankings and
spatial activity profiles to support data-driven scouting decisions.

## Value Proposition

ScoutDash moves beyond generic box-score statistics. It leverages StatsBomb
coordinates to calculate advanced KPIs such as Progressive Passes, Penalty Area
entries, and spatial third-by-third involvement, allowing technical directors to
rank players against specific tactical systems.

## Core Functionalities

- **Data ingestion**: Direct integration with `statsbombpy` for access to open
  competitions (La Liga, World Cup, FA WSL, and others).
- **Tactical fit scoring**: A transparent, weighted engine (0-100) that ranks
  players against pre-defined role templates (for example, Ball-Playing Centre
  Back, Pressing Forward).
- **Spatial profiling**: Third-by-third action counts (defensive, middle, final)
  plus a Gaussian KDE pitch heatmap of event locations.
- **Explainable analytics**: Each ranking includes a contribution breakdown and
  rule-based scouting notes.
- **Comparison engine**: Side-by-side radar charts and category leadership for up
  to five players.

## Metrics

Counting stats are aggregated per player from match events, then normalized to
per-90 values and ranked into percentiles before scoring. Notable metrics:

- Penalties are tracked separately. `np_shots`, `np_shots_on_target`, `np_xg`,
  and `np_goals` exclude penalties so shot-volume metrics stay penalty-consistent.
- `xg_per_shot` is computed from non-penalty xG over non-penalty shots, so a
  single penalty (xG ~0.79) cannot distort a player's average shot quality.
- Percentile normalization uses rank percentiles, which are robust to outliers.

See the in-app Metric Guide (or `src/glossary.py`) for definitions, tactical
rationale, and calculation method for every metric.

## Project Architecture

```text
app.py                # Dashboard UI and user flow
src/
  data_loader.py      # StatsBomb ingestion, vectorized event aggregation, schema checks
  metrics.py          # Per-90 normalization and category logic
  scoring.py          # Role weighting and Fit Score calculation
  transforms.py       # Position mapping, percentile normalization, filters
  insights.py         # Rule-based recruitment notes
  comparison.py       # Multi-player analysis logic
  glossary.py         # Metric definitions and tactical rationale
  visuals.py          # Plotly and mplsoccer chart templates
  style.py            # Color tokens, CSS chrome, HTML-escaping helpers
tests/
  test_core_logic.py  # Unit and regression tests
STYLEGUIDE.md         # Visual design system reference
requirements.txt      # Runtime dependencies
requirements-dev.txt  # Runtime + test dependencies
```

## Setup and Installation

1. Clone and create an environment:
   ```bash
   git clone https://github.com/yourusername/scout-dash.git
   cd scout-dash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. Install runtime dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the dashboard:
   ```bash
   streamlit run app.py
   ```

## Development

Install the development dependencies (runtime plus pytest) and run the tests:

```bash
pip install -r requirements-dev.txt
pytest
```

The test suite covers the scoring math, percentile normalization, and the
event-aggregation logic, including regression tests for known parsing bugs.

## Roadmap

- Full-season aggregation with caching improvements.
- Expected Threat (xT) and pass clustering.
