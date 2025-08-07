{{ config(
    materialized='table',
    database='HEALTHCARE_ANALYTICS',
    schema='silver',
    alias='silver_workload_distribution'
) }}

SELECT 
    facility_id,
    facility_name,
    state,
    work_date,
    rn_hours,
    lpn_hours, 
    cna_hours,
    (rn_hours + lpn_hours + cna_hours) as total_nursing_hours,
    ROUND(rn_hours / NULLIF((rn_hours + lpn_hours + cna_hours), 0) * 100, 1) as rn_percentage,
    ROUND(lpn_hours / NULLIF((rn_hours + lpn_hours + cna_hours), 0) * 100, 1) as lpn_percentage,
    ROUND(cna_hours / NULLIF((rn_hours + lpn_hours + cna_hours), 0) * 100, 1) as cna_percentage
FROM {{ ref('silver_nursing_staffing_cleaned') }}
WHERE (rn_hours + lpn_hours + cna_hours) > 0
