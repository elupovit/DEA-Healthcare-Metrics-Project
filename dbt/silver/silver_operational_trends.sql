{{ config(
    materialized='table',
    database='HEALTHCARE_ANALYTICS',
    schema='silver',
    alias='silver_operational_trends'
) }}

SELECT
    facility_id,
    facility_name,
    state,
    work_date,
    EXTRACT(MONTH FROM work_date) as month,
    EXTRACT(DOW FROM work_date) as day_of_week,
    patient_census,
    (rn_hours + lpn_hours + cna_hours) as total_nursing_hours,
    ROUND((rn_hours + lpn_hours + cna_hours) / NULLIF(patient_census, 0), 2) as efficiency_ratio
FROM {{ ref('silver_nursing_staffing_cleaned') }}
WHERE patient_census > 0
