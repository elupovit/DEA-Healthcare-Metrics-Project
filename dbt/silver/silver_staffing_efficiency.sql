{{ config(
    materialized='table',
    database='HEALTHCARE_ANALYTICS',
    schema='silver',
    alias='silver_staffing_efficiency'
) }}

SELECT
    facility_id,
    facility_name,
    state,
    work_date,
    ROUND(rn_hours / NULLIF(patient_census, 0), 2) as rn_hours_per_patient,
    ROUND(lpn_hours / NULLIF(patient_census, 0), 2) as lpn_hours_per_patient,
    ROUND(cna_hours / NULLIF(patient_census, 0), 2) as cna_hours_per_patient,
    ROUND((rn_hours + lpn_hours + cna_hours) / NULLIF(patient_census, 0), 2) as total_nursing_hours_per_patient
FROM {{ ref('silver_nursing_staffing_cleaned') }}
WHERE patient_census > 0
