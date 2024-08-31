import aioboto3

# Initialize the client and session globally
s3_client = None
session = None


async def get_s3_client():
    global s3_client, session
    if s3_client is None or session is None:
        session = aioboto3.Session()
        s3_client = await session.client("s3").__aenter__()
    return s3_client


async def close_s3_client():
    global s3_client, session
    if s3_client is not None:
        await s3_client.__aexit__(None, None, None)
        s3_client = None
    if session is not None:
        await session.__aexit__(None, None, None)
        session = None
