import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

# Page configuration
st.set_page_config(
    page_title="Healthcare Analytics Dashboard",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Healthcare Analytics Dashboard")
st.markdown("### Real-time Nursing Staffing & Performance Insights")

def connect_to_snowflake(acct, usr, pwd, role, wh, db, schema):
    try:
        ctx = snowflake.connector.connect(  
            user=usr,
            password=pwd,
            account=acct,
            role=role,
            warehouse=wh,
            database=db,
            schema=schema  
        )
        cs = ctx.cursor()
        st.session_state['snow_conn'] = cs
        st.session_state['is_ready'] = True
        return cs
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")
        st.session_state['is_ready'] = False
        return None

@st.cache_data(ttl=600)
def get_facility_data():
    query = 'SELECT * FROM GOLD_FACILITY_PERFORMANCE_SUMMARY;'
    results = st.session_state['snow_conn'].execute(query)
    results = st.session_state['snow_conn'].fetch_pandas_all()
    return results

@st.cache_data(ttl=600)
def get_state_data():
    query = 'SELECT * FROM GOLD_STATE_BENCHMARKS;'
    results = st.session_state['snow_conn'].execute(query)
    results = st.session_state['snow_conn'].fetch_pandas_all()
    return results

# Sidebar for connection
st.sidebar.header("🔗 Snowflake Connection")
st.sidebar.markdown("Enter your credentials:")

with st.sidebar:
    account = st.text_input("Account", value="qfc25435.us-east-1")
    username = st.text_input("Username", value="EITANLUPO94") 
    password = st.text_input("Password", type="password")
    role = st.text_input("Role", value="ACCOUNTADMIN")
    warehouse = st.text_input("Warehouse", value="COMPUTE_WH")
    database = st.text_input("Database", value="HEALTHCARE_ANALYTICS")
    schema = st.text_input("Schema", value="GOLD")
    
    connect = st.button(
        "🚀 Connect to Snowflake",
        on_click=connect_to_snowflake,
        args=(account, username, password, role, warehouse, database, schema)
    )

# Initialize connection state
if 'is_ready' not in st.session_state:
    st.session_state['is_ready'] = False

# Main dashboard content
if st.session_state['is_ready']:
    st.sidebar.success("✅ Connected!")
    
    try:
        # Load data
        facility_df = get_facility_data()
        state_df = get_state_data()
        
        # Success message with data summary
        st.success(f"📊 Loaded {len(facility_df)} facilities across {len(state_df)} states")
        
        # Key Performance Indicators
        st.markdown("## 📈 Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_hours = facility_df['AVG_HOURS_PER_PATIENT'].mean()
            st.metric(
                label="Avg Hours/Patient",
                value=f"{avg_hours:.2f}",
                help="Average nursing hours per patient across all facilities"
            )
        
        with col2:
            total_facilities = len(facility_df)
            st.metric(
                label="Total Facilities",
                value=f"{total_facilities:,}",
                help="Number of healthcare facilities analyzed"
            )
            
        with col3:
            avg_contract = facility_df['AVG_CONTRACT_PERCENTAGE'].mean()
            st.metric(
                label="Avg Contract Staff %",
                value=f"{avg_contract:.1f}%",
                help="Average percentage of contract vs employee staff"
            )
            
        with col4:
            avg_census = facility_df['AVG_PATIENT_CENSUS'].mean()
            st.metric(
                label="Avg Patient Census",
                value=f"{avg_census:.0f}",
                help="Average number of patients per facility"
            )
        
        # Create tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏥 Facility Performance", 
            "🗺️ State Analysis", 
            "📊 Staffing Analysis",
            "📋 Data Tables"
        ])
        
        with tab1:
            st.markdown("## 🏥 Facility Performance Rankings")
            
            # State filter
            states = ['All States'] + sorted(facility_df['STATE'].unique().tolist())
            selected_state = st.selectbox("Filter by State:", states, key="facility_state_filter")
            
            # Filter data
            if selected_state != 'All States':
                filtered_df = facility_df[facility_df['STATE'] == selected_state]
            else:
                filtered_df = facility_df
            
            # Performance analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🟢 Most Efficient Facilities")
                st.caption("Lowest nursing hours per patient")
                
                top_performers = filtered_df.nsmallest(10, 'AVG_HOURS_PER_PATIENT')
                
                if len(top_performers) > 0:
                    fig_top = px.bar(
                        top_performers,
                        x='AVG_HOURS_PER_PATIENT',
                        y='FACILITY_NAME',
                        orientation='h',
                        color='AVG_HOURS_PER_PATIENT',
                        color_continuous_scale='Greens_r',
                        title="Top 10 Most Efficient Facilities"
                    )
                    fig_top.update_layout(
                        height=400, 
                        showlegend=False,
                        yaxis_title="",
                        xaxis_title="Hours per Patient"
                    )
                    st.plotly_chart(fig_top, use_container_width=True)
                else:
                    st.info("No data available for selected state")
            
            with col2:
                st.markdown("### 🔴 Least Efficient Facilities")
                st.caption("Highest nursing hours per patient")
                
                bottom_performers = filtered_df.nlargest(10, 'AVG_HOURS_PER_PATIENT')
                
                if len(bottom_performers) > 0:
                    fig_bottom = px.bar(
                        bottom_performers,
                        x='AVG_HOURS_PER_PATIENT',
                        y='FACILITY_NAME',
                        orientation='h',
                        color='AVG_HOURS_PER_PATIENT',
                        color_continuous_scale='Reds',
                        title="Top 10 Least Efficient Facilities"
                    )
                    fig_bottom.update_layout(
                        height=400, 
                        showlegend=False,
                        yaxis_title="",
                        xaxis_title="Hours per Patient"
                    )
                    st.plotly_chart(fig_bottom, use_container_width=True)
                else:
                    st.info("No data available for selected state")
        
        with tab2:
            st.markdown("## 🗺️ State-Level Healthcare Performance")
            
            # State comparison chart
            fig_states = px.bar(
                state_df.sort_values('STATE_AVG_HOURS_PER_PATIENT'),
                x='STATE',
                y='STATE_AVG_HOURS_PER_PATIENT',
                color='STATE_AVG_HOURS_PER_PATIENT',
                color_continuous_scale='RdYlBu_r',
                title="Average Nursing Hours per Patient by State",
                labels={
                    'STATE_AVG_HOURS_PER_PATIENT': 'Hours per Patient',
                    'STATE': 'State'
                }
            )
            fig_states.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig_states, use_container_width=True)
            
            # State performance metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                best_state = state_df.loc[state_df['STATE_AVG_HOURS_PER_PATIENT'].idxmin()]
                st.success(f"**🥇 Most Efficient State**\n\n{best_state['STATE']}\n\n{best_state['STATE_AVG_HOURS_PER_PATIENT']:.2f} hours/patient")
            
            with col2:
                worst_state = state_df.loc[state_df['STATE_AVG_HOURS_PER_PATIENT'].idxmax()]
                st.error(f"**📈 Least Efficient State**\n\n{worst_state['STATE']}\n\n{worst_state['STATE_AVG_HOURS_PER_PATIENT']:.2f} hours/patient")
            
            with col3:
                efficiency_gap = worst_state['STATE_AVG_HOURS_PER_PATIENT'] - best_state['STATE_AVG_HOURS_PER_PATIENT']
                st.info(f"**📊 Efficiency Gap**\n\n{efficiency_gap:.2f} hours/patient\n\nDifference between best and worst performing states")
        
        with tab3:
            st.markdown("## 📊 Staffing Analysis")
            
            # Contract vs efficiency analysis
            st.markdown("### Contract Staffing vs Efficiency")
            
            fig_scatter = px.scatter(
                facility_df,
                x='AVG_CONTRACT_PERCENTAGE',
                y='AVG_HOURS_PER_PATIENT',
                color='STATE',
                size='AVG_PATIENT_CENSUS',
                hover_data=['FACILITY_NAME'],
                title="Relationship between Contract Staffing and Efficiency",
                labels={
                    'AVG_CONTRACT_PERCENTAGE': 'Contract Staff Percentage (%)',
                    'AVG_HOURS_PER_PATIENT': 'Hours per Patient',
                    'AVG_PATIENT_CENSUS': 'Patient Census'
                }
            )
            fig_scatter.update_layout(height=500)
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # RN percentage distribution
            st.markdown("### RN Staffing Distribution")
            
            fig_rn = px.histogram(
                facility_df,
                x='AVG_RN_PERCENTAGE',
                nbins=25,
                title="Distribution of RN Staffing Percentage Across Facilities",
                labels={
                    'AVG_RN_PERCENTAGE': 'RN Percentage (%)',
                    'count': 'Number of Facilities'
                }
            )
            fig_rn.update_layout(height=400)
            st.plotly_chart(fig_rn, use_container_width=True)
            
            # Insights section
            st.markdown("### 🔍 Key Insights")
            
            # Contract staffing analysis
            high_contract = facility_df[facility_df['AVG_CONTRACT_PERCENTAGE'] > 30]
            low_contract = facility_df[facility_df['AVG_CONTRACT_PERCENTAGE'] <= 30]
            
            if len(high_contract) > 0 and len(low_contract) > 0:
                high_avg = high_contract['AVG_HOURS_PER_PATIENT'].mean()
                low_avg = low_contract['AVG_HOURS_PER_PATIENT'].mean()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        label="High Contract Facilities (>30%)",
                        value=f"{high_avg:.2f} hrs/patient",
                        help=f"Average efficiency for {len(high_contract)} facilities with >30% contract staff"
                    )
                
                with col2:
                    st.metric(
                        label="Low Contract Facilities (≤30%)",
                        value=f"{low_avg:.2f} hrs/patient",
                        delta=f"{low_avg - high_avg:.2f}",
                        help=f"Average efficiency for {len(low_contract)} facilities with ≤30% contract staff"
                    )
                
                if high_avg > low_avg:
                    st.warning(f"💡 **Insight**: Facilities with higher contract staff usage show {high_avg - low_avg:.2f} more hours per patient on average, suggesting potential efficiency challenges with contract staffing.")
                else:
                    st.success(f"💡 **Insight**: Facilities with higher contract staff usage are {low_avg - high_avg:.2f} hours more efficient per patient, indicating effective contract staff utilization.")
        
        with tab4:
            st.markdown("## 📋 Data Tables")
            
            # Facility data table
            st.markdown("### Facility Performance Data")
            st.caption(f"Complete data for {len(facility_df)} healthcare facilities")
            
            # Add search functionality
            search_term = st.text_input("🔍 Search facilities:", placeholder="Enter facility name or state...")
            
            if search_term:
                filtered_table = facility_df[
                    facility_df['FACILITY_NAME'].str.contains(search_term, case=False, na=False) |
                    facility_df['STATE'].str.contains(search_term, case=False, na=False)
                ]
            else:
                filtered_table = facility_df
            
            # Sort options
            sort_column = st.selectbox(
                "Sort by:",
                ['AVG_HOURS_PER_PATIENT', 'AVG_CONTRACT_PERCENTAGE', 'AVG_PATIENT_CENSUS', 'FACILITY_NAME'],
                key="sort_option"
            )
            
            sort_order = st.radio("Sort order:", ['Ascending', 'Descending'], horizontal=True)
            
            if sort_order == 'Ascending':
                filtered_table = filtered_table.sort_values(sort_column)
            else:
                filtered_table = filtered_table.sort_values(sort_column, ascending=False)
            
            st.dataframe(filtered_table, use_container_width=True, height=400)
            
            # State benchmarks table
            st.markdown("### State Benchmark Data")
            st.caption(f"Comparative performance across {len(state_df)} states")
            
            state_table = state_df.sort_values('STATE_AVG_HOURS_PER_PATIENT')
            st.dataframe(state_table, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please check your connection and try again.")

else:
    # Show connection prompt
    st.warning("⚠️ Please connect to Snowflake using the sidebar to view your healthcare analytics.")
    
    # Show architecture info while disconnected
    st.markdown("### 🏗️ Your Enterprise Data Pipeline")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📊 Data Sources**
        - Google Drive (20+ healthcare files)
        - 1.3M+ nursing records
        - Quality & performance metrics
        """)
    
    with col2:
        st.markdown("""
        **⚙️ Processing Pipeline**
        - Lambda (2 AM daily sync)
        - Snowflake (Bronze → Silver → Gold)
        - dbt (Advanced transformations)
        """)
    
    with col3:
        st.markdown("""
        **📈 Analytics Ready**
        - Facility performance rankings
        - State-level benchmarks
        - Staffing efficiency insights
        """)
    
    st.info("🎯 **Your complete healthcare analytics platform is ready!** Connect above to explore nursing staffing insights and facility performance metrics.")

# Footer
st.markdown("---")
st.markdown("**🏥 Healthcare Analytics Dashboard** | Built with Streamlit, Snowflake & dbt | Real-time healthcare insights")
