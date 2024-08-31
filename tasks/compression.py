import os
import uuid
import json
import asyncio
from io import BytesIO
from urllib.parse import ParseResult, urlunparse

import requests
import aiohttp
from PIL import Image

from .configs import get_s3_client

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "my-bucket")


async def s3_upload(
    s3_client,
    bucket_name: str,
    image_key: str,
    image_data: bytes | None
):
    """Single image upload"""
    if image_data is None:
        return None

    await s3_client.put_object(
        Bucket=bucket_name,
        Key=image_key,
        Body=image_data,
    )
    return image_key


def compress_image(image_data, quality=50):
    """Compress image using Pillow and return compressed image"""
    if not image_data:
        return None

    with Image.open(BytesIO(image_data)) as img:
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality)
        return output.getvalue()


async def upload_data_to_s3(s3_client, data: dict):
    """Uploads a row data of csv to s3 (also calls the compression logic)"""

    org_images: list = data["urls"]
    images: list = data["output_images"]
    tasks = []
    newly_generated_urls = []
    for org_img, img in zip(org_images, images):
        compressed_image = compress_image(img)
        image_path = org_img.path

        if "." in image_path[-5:]:
            splited_name = org_img.rsplit(".", 1)
            image_key = f"{splited_name[0]}_compressed.{splited_name[1]}"
        elif image_path:
            image_key = f"{image_path}_compressed"
        else:
            uid = uuid.uuid3(uuid.NAMESPACE_DNS, org_img.netloc)
            image_key = f"{uid}_compressed"

        newly_generated_urls.append(image_key)
        tasks.append(
            s3_upload(
                s3_client, S3_BUCKET_NAME, image_key, compressed_image
            )
        )

    return await asyncio.gather(*tasks)


async def single_row_image_process(
    session: aiohttp.ClientSession, data: dict
):
    """Takes one row of image from csv"""

    urls: list[ParseResult] = data.get("urls", [])
    responses = []
    for url in urls:
        url = urlunparse(url)
        responses.append(session.get(url))

    responses: list[aiohttp.ClientResponse] = await asyncio.gather(**responses)
    for i, res in enumerate(responses):
        responses[i] = res.read() if res.status == 200 else None

    data["output_images"] = responses
    return data


async def start_image_compression(bulk_data: list[dict]):
    """Async start point for image compression and storage"""
    with aiohttp.ClientSession() as session:
        tasks = []
        for data in bulk_data:
            tasks.append(single_row_image_process(session, data))

        updated_data = await asyncio.gather(*tasks)
        tasks = []
        for data in updated_data:
            tasks.append(s3_upload(get_s3_client(), data))

    return await asyncio.gather(*tasks)


def bulk_image_compression(data: dict):
    """RQ Job/Task which will be triggered when job is enqueued"""

    callback: str = data["callback"]
    data: list[dict] = data["data"]

    status = {}
    try:
        asyncio.run(start_image_compression(data))
    except Exception:
        status = {"status": "error"}

    if not status:
        status = {"status": "completed"}

    # Send callback if the data processed successfully
    requests.post(callback, json=data)

    return json.dumps({
        **status,
        "message": "Task Completed",
    })
