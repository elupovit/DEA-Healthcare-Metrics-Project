# AWS Lambda Data Pipeline

## Overview
Serverless data ingestion pipeline that syncs healthcare data from Google Drive to S3 on a daily schedule.

## Features
- **Automated Daily Sync**: Scheduled execution at 2:00 AM EST
- **Incremental Processing**: Only processes changed files
- **State Management**: Tracks last run timestamps
- **Error Handling**: Robust retry and logging mechanisms

## Setup Instructions

### Google Drive API Setup
1. Create a Google Cloud Project
2. Enable Google Drive API
3. Create a Service Account
4. Download the JSON credentials file
5. Store credentials securely (AWS Secrets Manager recommended)

### Security Note
⚠️ Never commit actual credential files to version control!
Use the template file and replace with your actual values.
