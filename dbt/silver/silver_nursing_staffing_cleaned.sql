{{ config(
    materialized='table',
    database='HEALTHCARE_ANALYTICS',
    schema='silver',
    alias='silver_nursing_staffing_cleaned'
) }}

SELECT 
    PROVNUM as facility_id,
    PROVNAME as facility_name,
    STATE,
    TRY_CAST(WORKDATE AS DATE) as work_date,
    COALESCE(HRS_RN, 0) as rn_hours,
    COALESCE(MDSCENSUS, 0) as patient_census,
    COALESCE(HRS_LPN, 0) as lpn_hours,
    COALESCE(HRS_CNA, 0) as cna_hours,
    COALESCE(HRS_RN_emp, 0) as rn_emp_hours,
    COALESCE(HRS_RN_ctr, 0) as rn_contract_hours,
    COALESCE(HRS_LPN_emp, 0) as lpn_emp_hours,
    COALESCE(HRS_LPN_ctr, 0) as lpn_contract_hours,
    COALESCE(HRS_CNA_emp, 0) as cna_emp_hours,
    COALESCE(HRS_CNA_ctr, 0) as cna_contract_hours
FROM {{ source('bronze', 'PBJ_Daily_Nurse_Staffing_Q2_2024') }}
WHERE PROVNUM IS NOT NULL
