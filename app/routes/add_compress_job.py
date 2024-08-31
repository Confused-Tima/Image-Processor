from io import StringIO, BytesIO

import pandas as pd
import pandera as pa
from rq.job import JobStatus
from fastapi import APIRouter, UploadFile, File, Depends

from app.logger import logger
from app.configs import RQueues
from app.security.authenticate import authenticate_api_key
from app.exceptions.custom_http_exceptions import raise_HTTP_422
from redis_connection.add_job import enqueue_job, RedisConnection
from app.utils.common_utils import csv_urls_converter, df_converter
from app.schemas.compression_schema import (
    csv_schema,
    JobStatusRequest,
    JobStatusResponse,
    CompressionJobResponse,
)

router = APIRouter()

redis_conn = RedisConnection()

csv_file_required_fields = {
    "sno": "int",
    "name": "str",
    "urls": "str",
}
req_fields = ", ".join(
    f"{field} : {dtype}" for field, dtype in csv_file_required_fields.items()
)


@router.post(
    "/v1/compress-images",
    dependencies=[Depends(authenticate_api_key)],
)
def add_job_with_file(
    file: UploadFile = File(
        description=(
            f"Give all required fields({req_fields}) "
            "with correct spellings and values. Columns must strictly "
            "adhere to predefined data types."
        )
    ),
):
    """API to create compression job from file"""

    file_content = file.file.read()
    if file.filename.endswith("csv"):
        df = pd.read_csv(StringIO(file_content.decode("utf-8")))
    elif file.filename.endswith("xlsx"):
        df = pd.read_excel(BytesIO(file_content))

    df.fillna("", inplace=True)
    df_converter(df, "urls", csv_urls_converter)

    try:
        csv_schema.validate(df)
    except pa.errors.SchemaError as e:
        logger.error(f"Error validating the csv fields:: pandera error -> {str(e)}")
        raise_HTTP_422(["File Fields"], str(e), "Validation Error")

    data = df.to_dict(orient="records")
    return CompressionJobResponse(
        job_id=enqueue_job(
            RQueues.IMAGE_PROCESSING_Q,
            {"data": data},
        ),
        job_status=JobStatus.QUEUED
    )


@router.post(
    "/v1/fetch-job-status",
    dependencies=[Depends(authenticate_api_key)],
)
def get_job_status(status_req: JobStatusRequest):
    status = redis_conn.get_job_status(status_req.job_id)
    created_at = (
        status.created_at.isoformat()
        if status.created_at
        else status.created_at
    )
    started_at = (
        status.started_at.isoformat()
        if status.started_at
        else status.started_at
    )

    ended_at = (
        status.ended_at.isoformat()
        if status.ended_at
        else status.ended_at
    )

    error = (
        str(status.error)
        if status.error
        else status.error
    )

    return JobStatusResponse(
        result=status.result,
        created_at=created_at,
        started_at=started_at,
        ended_at=ended_at,
        error=error
    )
