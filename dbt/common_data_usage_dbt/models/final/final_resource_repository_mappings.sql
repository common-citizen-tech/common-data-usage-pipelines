{{ config(materialized='table') }}

SELECT
    resources.id as resource_id,
    search_results.repository,
    resources.dataset_id,
    resources.organization_id
FROM
    {{ref('final_clean_all_resources')}} resources
JOIN {{ ref('final_sourcegraph_search_results') }} search_results
ON resources.url = search_results.resource_url
