# -*- coding: utf-8 -*-
from typing import Dict

from . import RedisConnection
from .configs import RQueues, redis_settings
from tasks.compression import bulk_image_compression

redis_conn = RedisConnection()


def enqueue_job(q: RQueues, data: Dict[str, any], **kwargs) -> str:
    """
    General method to enqueue any data to the specified queue.

    Parameters
    ----------
    q : RQueues
        Queue name
    data : Dict[str, any]

    Returns
    -------
    str
    """
    local_kwargs = {
        "result_ttl": redis_settings.results_persistance,
        "job_timeout": redis_settings.job_timeout,
        **kwargs
    }
    job = redis_conn[q].enqueue(bulk_image_compression, data, **local_kwargs)
    return job.get_id()
