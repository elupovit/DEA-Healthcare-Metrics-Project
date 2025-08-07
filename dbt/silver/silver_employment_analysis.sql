{{ config(
    materialized='table',
    database='HEALTHCARE_ANALYTICS',
    schema='silver',
    alias='silver_employment_analysis'
) }}

SELECT
    facility_id,
    facility_name,
    state,
    work_date,
    (rn_emp_hours + lpn_emp_hours + cna_emp_hours) as total_employee_hours,
    (rn_contract_hours + lpn_contract_hours + cna_contract_hours) as total_contract_hours,
    ROUND((rn_contract_hours + lpn_contract_hours + cna_contract_hours)/ NULLIF((rn_emp_hours + lpn_emp_hours + cna_emp_hours), 0) * 100, 1) as contract_percentage
FROM {{ ref('silver_nursing_staffing_cleaned') }}
