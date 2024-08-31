# -*- coding: utf-8 -*-
from typing import Any, Union, TypeAlias, Dict

import redis
from rq import Queue
from rq.job import Job
from rq.exceptions import NoSuchJobError

from global_utils import SingletonMeta
from .configs import RQueues, redis_settings, CustomJobStatus

Q: TypeAlias = Union[RQueues, str]


class RedisConnection(metaclass=SingletonMeta):
    """Redis connection manager"""
    def __init__(self) -> None:
        self.redis = redis.from_url(
            redis_settings.redis_url, encoding="utf8"
        )
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
                status=job.get_status()
            )
        except NoSuchJobError as e:
            job_status = CustomJobStatus(error=str(e))
        except Exception as e:
            return CustomJobStatus(error=str(e))

        return job_status

    def shutdown(self) -> None:
        self.redis.close()
