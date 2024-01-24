import logging

import luigi
import sentry_sdk

from common_data_usage_pipelines.sentry import init_sentry

init_sentry()

logger = logging.Logger(__name__)


# https://stackoverflow.com/a/40656485
@luigi.Task.event_handler(luigi.Event.FAILURE)
def mourn_failure(task: luigi.Task, exception: Exception):
    sentry_sdk.capture_exception(exception, extra=dict(task=repr(task)))
    logger.critical("Error occurred: {e}".format(e=exception))
