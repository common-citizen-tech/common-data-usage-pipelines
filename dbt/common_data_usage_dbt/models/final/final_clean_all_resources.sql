{{ config(materialized='table') }}


select
    resources.*,
    datasets.id as dataset_id,
    organizations.id as organization_id
from {{ source('ckan_api_clean', 'ckan_clean_all_resources') }} resources
LEFT JOIN {{ ref('final_clean_datasets') }} datasets
ON resources.package_id = datasets.id
LEFT JOIN {{ ref('final_clean_organizations') }} organizations
ON datasets.owner_org = organizations.id
