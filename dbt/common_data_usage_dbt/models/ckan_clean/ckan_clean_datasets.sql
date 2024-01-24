{{ config(materialized='table') }}

with package_ids as (
    select distinct package_id
    from {{ ref('ckan_clean_json_resources') }}
),
source_data as (
    select
      raw_datasets.*
    from
      {{ source('ckan_api_raw', 'ckan_datasets') }} raw_datasets
    join
      package_ids
    on
      raw_datasets.id = package_ids.package_id
)

select * from source_data
