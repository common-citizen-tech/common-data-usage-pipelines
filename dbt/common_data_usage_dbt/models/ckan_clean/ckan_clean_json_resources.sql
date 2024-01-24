{{ config(materialized='table') }}

with source_data as (
    select
        *
    from {{ ref('ckan_clean_all_resources') }}
    where contains(lower(format), 'json')
)

select * from source_data