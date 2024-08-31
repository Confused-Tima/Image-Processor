# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any, Union, TypeAlias, Dict

import redis
from rq import Queue
from pydantic import BaseModel
from rq.job import Job
from rq.exceptions import NoSuchJobError

from app.configs import settings, RQueues
from app.utils.common_utils import SingletonMeta

Q: TypeAlias = Union[RQueues, str]


class CustomJobStatus(BaseModel):
    result: Union[str | None] = None
    created_at: Union[datetime | None] = None
    started_at: Union[datetime | None] = None
    ended_at: Union[datetime | None] = None
    error: Union[NoSuchJobError | None] = None


class RedisConnection(metaclass=SingletonMeta):
    """Redis connection manager"""
    def __init__(self) -> None:
        self.redis = redis.ConnectionPool.from_url(settings.redis_url, encoding="utf8")
        self._queues = {
            q.value: Queue(q.value, connection=self.redis)
            for q in RQueues.__members__.values()
        }

    def __call__(self, *args, **kwds) -> Any:
        """
        If need to call the redis connection itself.
        Then it can be called using the current object.

        Returns
        -------
        Any
        """
        return self.redis(*args, **kwds)

    def get_all_queues(self) -> Dict[str, Queue]:
        return self._queues

    def __getitem__(self, queue: Q) -> Queue:
        """
        Lets us use obj["queue_name"]

        Parameters
        ----------
        queue : Q
            queue name. Best if picked from RQueues Enum

        Returns
        -------
        Queue

        Raises
        ------
        ValueError
        """
        if isinstance(queue, RQueues):
            queue = queue.value

        if queue in self._queues:
            return self._queues[queue]

        raise ValueError(f"No queue named: {queue} exists")

    def get_queue(self, queue: Q, default: Any = None) -> Queue | Any:
        """
        Fetches the asked queue with defaults

        Parameters
        ----------
        queue : Q
            queue name. Best if picked from RQueues Enum
        default : Any, optional

        Returns
        -------
        Queue | None
        """
        return self._queues.get(queue, default)

    def get_job_status(self, job_id: str):
        try:
            job = Job.fetch(job_id, self.redis)
            job_status = CustomJobStatus(
                result=job.result,
                created_at=job.created_at,
                started_at=job.started_at,
                ended_at=job.ended_at,
            )
        except NoSuchJobError as e:
            job_status = CustomJobStatus(error=e)

        return job_status

    def shutdown(self) -> None:
        self.redis.close()


def dummy_task(*args, **kwargs):
    return None
