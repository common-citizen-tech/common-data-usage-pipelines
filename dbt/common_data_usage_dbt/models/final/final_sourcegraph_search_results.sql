{{ config(materialized='table') }}


select * from {{ source('sourcegraph_for_all', 'sourcegraph_search_results') }}