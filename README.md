# DEA-Healthcare-Metrics-Project

# Healthcare Analytics Dashboard

## Overview
Interactive Streamlit dashboard analyzing 14,522 healthcare facilities with real-time performance insights.

## Features
- **Facility Performance**: Rankings of most/least efficient facilities
- **State Analysis**: Cross-state healthcare benchmarking
- **Staffing Analysis**: Contract vs employee efficiency metrics
- **Data Explorer**: Searchable facility database

## Installation
```bash
pip install streamlit snowflake-connector-python pandas plotly
```

## Usage
```bash
streamlit run streamlit_app.py
```

## Configuration
1. Enter Snowflake credentials in sidebar
2. Connect to HEALTHCARE_ANALYTICS database
3. Access Gold layer analytics tables

## Data Sources
- `gold_facility_performance_summary` - 14,522 facility metrics
- `gold_state_benchmarks` - 50+ state comparisons

## Key Metrics
- Average nursing hours per patient
- Contract staff percentages
- Patient census data
- RN staffing ratios

Built with Streamlit + Plotly for enterprise-grade healthcare analytics.
