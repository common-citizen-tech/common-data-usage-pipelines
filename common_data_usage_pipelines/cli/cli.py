import os
import shutil
from datetime import datetime

import click
import luigi
from pydantic import BaseModel

from common_data_usage_pipelines.lib.artifacts_utils import get_artifact_filepath
from common_data_usage_pipelines.lib.ckan_api.raw_db import (
    create_raw_ckan_db_tables,
    create_raw_ckan_db_conn,
    RAW_CKAN_DATABASE_FILE,
)
from common_data_usage_pipelines.lib.ckan_api.download_datasets_info_tasks import (
    DownloadAllPackageSearchPagesTask,
)
from common_data_usage_pipelines.lib.ckan_api.insert_datasets_info_tasks import (
    InsertDatasetsInfoToDb,
)
from common_data_usage_pipelines.lib.config.site_config import (
    read_site_config_file,
    SiteConfig,
)
from common_data_usage_pipelines.lib.github.code_search.code_search_lr_tasks import (
    FetchGitHubCodeSearchApiResultsLRTask,
)
from common_data_usage_pipelines.lib.github.code_search.code_search_tasks import (
    FetchGitHubCodeSearchApiResultsMultiAcct,
)
from common_data_usage_pipelines.lib.sourcegraph.db import (
    create_sourcegraph_db_conn,
    create_sourcegraph_db_tables,
    SOURCEGRAPH_DATABASE_FILE,
)
from common_data_usage_pipelines.lib.sourcegraph.db_for_all import (
    create_sourcegraph_db_for_all_conn,
    create_sourcegraph_db_for_all_tables,
)
from common_data_usage_pipelines.lib.sourcegraph.download_sourcegraph_results_for_all_tasks import (
    FetchSourceGraphApiResultsForAll,
    SingleBatchFetchSourceGraphApiResultsForAllNoLimit,
)
from common_data_usage_pipelines.lib.sourcegraph.download_sourcegraph_results_tasks import (
    FetchSourceGraphApiResults,
)
from common_data_usage_pipelines.lib.sourcegraph.insert_sourcegraph_results_for_all_tasks import (
    InsertSourceGraphApiResultsForAll,
)
from common_data_usage_pipelines.lib.sourcegraph.insert_sourcegraph_results_tasks import (
    InsertSourceGraphResultsToDb,
)

import common_data_usage_pipelines.luigi_error_handler  # noqa: F401
from common_data_usage_pipelines.lib.sourcegraph.sourcegraph_results_for_all_deltalake_to_duckdb_tasks import (
    SourceGraphResultsForAllDeltaLakeToDuckDBTask,
)


class CliContextValue(BaseModel):
    site_config: SiteConfig


@click.group()
@click.option("--config-file", default=None, type=str)
@click.pass_context
def cli(ctx, config_file):
    if not config_file:
        config_file = os.environ.get("CONFIG_FILE")
    if not config_file:
        raise click.BadParameter(
            """
        Please provide a config file path via --config-file or CONFIG_FILE environment variable.
        """
        )

    ctx.obj = CliContextValue(site_config=read_site_config_file(config_file))


@cli.command()
@click.pass_obj
def download_datasets_info(ctx_val: CliContextValue):
    luigi.build(
        [
            DownloadAllPackageSearchPagesTask(
                package_search_endpoint_url=ctx_val.site_config.site.package_search_endpoint_url,
                site_short_name=ctx_val.site_config.site.short_name,
            )
        ],
        workers=50,
    )


@cli.command()
@click.pass_obj
def insert_datasets_info(ctx_val: CliContextValue):
    luigi.build(
        [
            InsertDatasetsInfoToDb(
                site_short_name=ctx_val.site_config.site.short_name,
            )
        ],
        workers=20,
    )
    formatted_date = datetime.now().strftime("%d_%m_%Y_%H:%M")
    shutil.copy2(
        RAW_CKAN_DATABASE_FILE,
        get_artifact_filepath(
            "read_only",
            ctx_val.site_config.site.short_name,
            f"ckan_api_{formatted_date}.db",
        ),
    )


@cli.command()
def create_raw_ckan_tables():
    con = create_raw_ckan_db_conn()
    create_raw_ckan_db_tables(con)


@cli.command()
@click.pass_obj
def download_sourcegraph_results(ctx_val: CliContextValue):
    luigi.build(
        [
            FetchSourceGraphApiResults(
                site_short_name=ctx_val.site_config.site.short_name,
            )
        ],
        workers=50,
    )


@cli.command()
@click.pass_obj
def download_github_code_search_results(ctx_val: CliContextValue):
    luigi.build(
        [
            FetchGitHubCodeSearchApiResultsMultiAcct(
                site_short_name=ctx_val.site_config.site.short_name,
            )
        ],
        workers=50,
    )


@cli.command()
def create_sourcegraph_tables():
    con = create_sourcegraph_db_conn()
    create_sourcegraph_db_tables(con)


@cli.command()
@click.pass_obj
def insert_sourcegraph_results(ctx_val: CliContextValue):
    luigi.build(
        [
            InsertSourceGraphResultsToDb(
                site_short_name=ctx_val.site_config.site.short_name,
            )
        ],
        workers=20,
    )
    formatted_date = datetime.now().strftime("%d_%m_%Y_%H:%M")
    shutil.copy2(
        SOURCEGRAPH_DATABASE_FILE,
        get_artifact_filepath(
            "read_only",
            ctx_val.site_config.site.short_name,
            f"sourcegraph_{formatted_date}.db",
        ),
    )


@cli.command()
@click.pass_obj
def download_sourcegraph_results_for_all(ctx_val: CliContextValue):
    luigi.build(
        [
            FetchSourceGraphApiResultsForAll(
                site_short_name=ctx_val.site_config.site.short_name,
            )
        ],
        workers=50,
    )


@cli.command()
@click.pass_obj
def download_sourcegraph_results_for_all_no_limit(ctx_val: CliContextValue):
    luigi.build(
        [
            SingleBatchFetchSourceGraphApiResultsForAllNoLimit(
                site_short_name=ctx_val.site_config.site.short_name,
            )
        ],
        workers=1,
    )


@cli.command()
@click.pass_obj
def download_github_code_search_results_lr(ctx_val: CliContextValue):
    luigi.build(
        [
            FetchGitHubCodeSearchApiResultsLRTask(
                site_short_name=ctx_val.site_config.site.short_name,
            )
        ],
        workers=1,
    )


@cli.command()
@click.pass_obj
def insert_sourcegraph_results_for_all(ctx_val: CliContextValue):
    luigi.build(
        [
            InsertSourceGraphApiResultsForAll(
                site_short_name=ctx_val.site_config.site.short_name,
            )
        ],
        workers=1,
    )


@cli.command()
@click.pass_obj
def sourcegraph_results_for_all_to_duckdb(ctx_val: CliContextValue):
    luigi.build(
        [
            SourceGraphResultsForAllDeltaLakeToDuckDBTask(
                site_short_name=ctx_val.site_config.site.short_name,
            )
        ],
        workers=1,
    )


@cli.command()
def create_sourcegraph_for_all_db_tables():
    con = create_sourcegraph_db_for_all_conn()
    create_sourcegraph_db_for_all_tables(con)


if __name__ == "__main__":
    cli()
