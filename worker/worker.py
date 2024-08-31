import os
import redis
from rq import Queue, Worker, Connection

from redis_connection.configs import redis_settings
from tasks.configs import close_s3_client


# Establish a connection to Redis
redis_conn = redis.from_url(redis_settings.redis_url)

HIGHQ = os.getenv("IMAGE_PROCESSING_Q", "image_processing_q")

queues = [
    Queue(HIGHQ, connection=redis_conn),
    # Queue("low", connection=redis_conn),
]


async def start():
    # Connect RQ to Redis and create a worker instance
    with Connection(redis_conn):
        worker = Worker(queues)
        worker.work()

    await close_s3_client()


if __name__ == "__main__":
    start()
