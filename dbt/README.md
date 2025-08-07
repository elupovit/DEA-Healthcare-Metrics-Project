# dbt Transformations

## Overview
Data transformations creating Silver and Gold layers from Bronze healthcare data.

## Models
- **Silver Layer**: 5 cleaned and standardized models
- **Gold Layer**: 2 aggregation models for dashboard

## Setup
1. Configure dbt Cloud with Snowflake connection
2. Set target database to HEALTHCARE_ANALYTICS
3. Configure custom schema macro for proper naming
4. Schedule daily runs at 3:00 AM EST

## Key Models
- `gold_facility_performance_summary` - 14,522 facility metrics
- `gold_state_benchmarks` - State-level comparisons

Transforms 1.3M+ raw records into business-ready analytics.
