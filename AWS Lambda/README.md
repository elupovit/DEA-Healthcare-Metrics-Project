# AWS Lambda Data Pipeline

## Overview
Serverless data ingestion pipeline that syncs healthcare data from Google Drive to S3 on a daily schedule.

## Features
- **Automated Daily Sync**: Scheduled execution at 2:00 AM EST
- **Incremental Processing**: Only processes changed files
- **State Management**: Tracks last run timestamps
- **Error Handling**: Robust retry and logging mechanisms

## Architecture
