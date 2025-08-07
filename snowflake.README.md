# Snowflake Data Warehouse Setup

## Overview
Medallion architecture implementation with automated Bronze → Silver → Gold data processing.

## Architecture
- **Bronze Layer**: Raw healthcare data (1.3M+ records)
- **Silver Layer**: Cleaned, standardized nursing metrics  
- **Gold Layer**: Business-ready analytics aggregations

## Files
- `healthcare-setup.sql` - Complete warehouse setup
- `automation-pipeline.sql` - Snowpipe and task automation
- `monitoring.sql` - Pipeline monitoring queries

## Quick Setup
1. Execute `healthcare-setup.sql` in Snowflake
2. Configure AWS credentials for S3 integration
3. Run `automation-pipeline.sql` for scheduled processing
4. Use `monitoring.sql` to verify pipeline status

## Tables Created
- 6 Bronze tables (raw data)
- 5 Silver models (dbt transformations)  
- 2 Gold tables (dashboard analytics)

## Scheduling
- Daily automated refresh at 2:15 AM EST
- Event-driven processing based on Lambda state
- Cost-optimized execution (only when new data available)
