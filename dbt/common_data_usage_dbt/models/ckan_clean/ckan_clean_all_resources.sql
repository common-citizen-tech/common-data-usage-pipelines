{{ config(materialized='table') }}

-- Unfortunately DuckDB driver doesn't support ephemeral materialization so we are forced to do this inline to reduce db size

with resources_cleaned_not_deduped as (
    select
        *
    from {{ source('ckan_api_raw', 'ckan_resources') }}
    where (
        id is not null and id != '' and
        package_id is not null and package_id != '' and
        url is not null and url != ''
    )
),
--https://duckdb.org/docs/sql/query_syntax/qualify.html
--https://github.com/dbt-labs/dbt-utils/blob/main/macros/sql/deduplicate.sql
source_data as (
    select *
    from resources_cleaned_not_deduped
    qualify
        row_number() over (
            partition by id
            order by name desc
        ) = 1
)

select * from source_data