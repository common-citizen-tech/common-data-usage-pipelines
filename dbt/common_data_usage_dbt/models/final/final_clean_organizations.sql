{{ config(materialized='table') }}

select * from {{ source('ckan_api_clean', 'ckan_clean_organizations') }}
