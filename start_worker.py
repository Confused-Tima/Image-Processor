import asyncio

from worker import worker


if __name__ == "__main__":
    asyncio.run(worker.start())
