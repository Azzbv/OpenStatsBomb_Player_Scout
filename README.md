# ScoutDash: Advanced Recruitment Analytics

A professional player recruitment dashboard built with **Python**, **Streamlit**, and **StatsBomb Open Data**. ScoutDash transforms raw event-level data into tactical fit rankings and spatial activity profiles to support data-driven scouting decisions.

## Value Proposition
ScoutDash moves beyond generic box-score statistics. It leverages StatsBomb coordinates to calculate advanced KPIs like **Progressive Passes**, **Penalty Area Involvement**, and **Spatial Dominance**, allowing technical directors to rank players based on specific tactical systems.

## Core Functionalities
- **Live Data Ingestion**: Direct integration with `statsbombpy` for real-time access to competitions (La Liga, World Cup, FA WSL, etc.).
- **Tactical Fit Scoring**: A transparent, weighted engine (0-100) that ranks players against pre-defined role templates (e.g., *Ball-Playing Centre Back*, *Pressing Forward*).
- **Spatial Profiling**: 3-Third Heatmaps (Defensive, Middle, Final) showing where players provide the most value in possession and defense.
- **Explainable Analytics**: Every ranking includes a contribution breakdown and rule-based scouting notes to ensure high interpretability.
- **Comparison Engine**: Side-by-side radar charts and category leadership tracking for up to 5 players.

## Project Architecture
```text
├── app.py                # Dashboard UI & User Flow
├── src/
│   ├── data_loader.py    # SB API ingestion & event aggregation
│   ├── metrics.py        # Per-90 normalization & category logic
│   ├── scoring.py        # Role weighting & Fit Score calculation
│   ├── insights.py       # Rule-based recruitment notes
│   ├── glossary.py       # Metric definitions & tactical rationale
│   ├── transforms.py     # Position mapping & normalization utils
│   ├── visuals.py        # Plotly radar & heatmap templates
│   └── comparison.py     # Multi-player analysis logic
├── requirements.txt      # Dependency list (StatsBomb, Plotly, etc.)
└── README.md             # Technical documentation
```

## ⚙️ Setup & Installation
1. **Clone & Environment**:
   ```bash
   git clone https://github.com/yourusername/scout-dash.git
   cd scout-dash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. **Install**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run**:
   ```bash
   streamlit run app.py
   ```

## ⚠️ Limitations & Roadmap
- **Sample Size**: Currently aggregates a subset of matches (default: 10) for performance. Future work will optimize for full-season aggregation.
- **Physical Data**: Does not currently include GPS/Tracking data (not available in Open Data).
- **Planned**: Integration of Expected Threat (xT) and Pass Clustering.
