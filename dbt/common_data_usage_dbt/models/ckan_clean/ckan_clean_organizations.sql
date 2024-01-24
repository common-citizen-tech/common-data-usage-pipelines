{{ config(materialized='table') }}

with owner_orgs as (
    select distinct owner_org
    from {{ ref('ckan_clean_datasets') }}
),
source_data as (
    select
      raw_organizations.*
    from
      {{ source('ckan_api_raw', 'ckan_organizations') }} raw_organizations
    join
      owner_orgs
    on
      raw_organizations.id = owner_orgs.owner_org
)

select * from source_data
