# Tesla Supercharger Network Analysis

This project models the Tesla Supercharger network in the United States as a graph and provides tools to explore its structure, connectivity, and regional coverage. It uses a cleaned and merged dataset of Supercharger locations and electric vehicle (EV) registration counts to support network analysis and visualization.

## Project Features

- Graph-based model of U.S. Supercharger stations
- Interactive shortest path calculator between stations
- Nearby charger search tool using real-world distances
- Network visualization using Streamlit and NetworkX
- Comparison of EV registration counts and station coverage by state

## Data Sources & Cleaning

Two public datasets were merged and cleaned:

1. **Supercharger Locations**  
   - Original file: `Supercharge Locations.csv`  
   - Cleaned to include only U.S. locations with valid geographic data

2. **EV Registration Counts by State**  
   - Original file: `10962-ev-registration-counts-by-state_9-06-24.csv`  
   - Standardized state formats and joined on state-level field

The final dataset, `merged_ev_supercharger_data.csv`, includes station-level details and EV adoption figures, enabling regional comparisons and infrastructure analysis.

## Files

- `tesla_ev.py`: Command-line version for graph analysis
- `tesla_ev_app.py`: Streamlit app for interactive exploration
- `merged_ev_supercharger_data.csv`: Cleaned and joined dataset
- `requirements.txt`: Python dependencies
- `README.md`: Project overview

## Running the App

To run the Streamlit app locally:

```bash
pip install -r requirements.txt
streamlit run tesla_ev_app.py
