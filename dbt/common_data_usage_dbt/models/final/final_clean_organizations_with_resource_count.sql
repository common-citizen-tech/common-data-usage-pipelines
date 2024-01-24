{{ config(materialized='table') }}

-- Unfortunately DuckDB driver doesn't support ephemeral materialization so we are forced to do this inline to reduce db size

with grouped_by_owner_org as (
    SELECT
        resources_by_dataset.owner_org,
        SUM(resources_by_dataset.resources_count) as values_count
    FROM {{ ref('final_clean_datasets_with_resource_count') }} resources_by_dataset
    GROUP BY owner_org
),
source_data as (
    SELECT
        ckan_clean_oranizations.*,
        grouped_by_owner_org.values_count AS resources_count,
    FROM grouped_by_owner_org
    LEFT JOIN {{ ref('final_clean_organizations') }} ckan_clean_oranizations
    ON grouped_by_owner_org.owner_org = ckan_clean_oranizations.id
    ORDER BY values_count DESC
)
select * from source_data