{{ config(materialized='table') }}

-- Unfortunately DuckDB driver doesn't support ephemeral materialization so we are forced to do this inline to reduce db size

with grouped_by_package_id as (
    SELECT
        ckan_clean_all_resources.package_id,
        COUNT(ckan_clean_all_resources.*) as values_count
    FROM {{ ref('final_clean_all_resources') }} ckan_clean_all_resources
    GROUP BY package_id
),
source_data as (
    SELECT
        ckan_clean_datasets.*,
        grouped_by_package_id.values_count AS resources_count,
    FROM grouped_by_package_id
    LEFT JOIN {{ ref('final_clean_datasets') }} ckan_clean_datasets
    ON grouped_by_package_id.package_id = ckan_clean_datasets.id
    ORDER BY values_count DESC
)
select * from source_data