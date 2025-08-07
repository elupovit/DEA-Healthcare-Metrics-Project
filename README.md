# DEA-Healthcare-Metrics-Project
# Healthcare Analytics Pipeline
*Enterprise-grade data platform processing 1.3M+ nursing records*

## 🏥 Project Overview
Complete healthcare analytics platform analyzing nursing staffing efficiency across 14,522 facilities. Automated pipeline transforms raw healthcare data into actionable business insights.

## 🚀 Live Results
- **1.3M+ Records Processed** ✅
- **14,522 Facilities Analyzed** ✅ 
- **50+ State Benchmarks** ✅
- **Real-time Dashboard** ✅

## 🏗️ Architecture
```
Google Drive → AWS Lambda → S3 → Snowflake → dbt → Streamlit
Raw Files      Daily 2AM     Bronze   Silver   Gold   Dashboard
(Healthcare)   Automation    Layer    Layer    Layer  Analytics
```

## 🛠️ Technology Stack
- **Cloud**: AWS Lambda, S3
- **Data Warehouse**: Snowflake (Medallion Architecture)
- **Transformations**: dbt Cloud
- **Dashboard**: Streamlit + Plotly
- **Scheduling**: Event-driven automation

## 📊 Key Features
- **Facility Performance Rankings**: Top/bottom performers by efficiency
- **State Benchmarking**: Cross-state healthcare comparisons  
- **Contract Staffing Analysis**: Optimization insights
- **Interactive Filtering**: Real-time data exploration
- **Automated Updates**: Daily pipeline execution

## 📁 Repository Structure
```
├── aws-lambda/          # Serverless data ingestion
├── snowflake/          # Data warehouse setup & automation
├── streamlit-dashboard/ # Interactive analytics interface
└── docs/               # Project documentation
```

## 🎯 Business Impact
- Identifies staffing inefficiencies across 14K+ facilities
- Enables data-driven healthcare resource optimization
- Provides state-level performance benchmarking
- Real-time monitoring of nursing productivity metrics

## ⚡ Quick Start
1. Review `/aws-lambda/` for data pipeline setup
2. Execute `/snowflake/` scripts for data warehouse
3. Deploy `/streamlit-dashboard/` for analytics interface

**Built with enterprise data engineering best practices**
