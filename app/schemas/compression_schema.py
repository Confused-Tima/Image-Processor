import pandera as pa
from urllib.parse import ParseResult

from pydantic import BaseModel
from rq.job import JobStatus


def check_list_of_urls(urls):
    """Validates the column for having list[<urls>]"""

    for url in urls:
        if (
            not url
            or not isinstance(url, list)
            or not all(isinstance(i, ParseResult) for i in url)
        ):
            return False
    return True


# Don't use urls check bcz will validating it while conversion
# Reduces looping
csv_schema = pa.DataFrameSchema(
    {
        "sno": pa.Column(int),
        "name": pa.Column(str),
        # "urls": pa.Column(object, checks=pandera_url_lists_check),
    }
)


class CompressionJobResponse(BaseModel):
    job_id: str
    job_status: JobStatus


class JobStatusRequest(BaseModel):
    job_id: str


class JobStatusResponse(BaseModel):
    status: str | None
    result: str | None
    created_at: str | None
    started_at: str | None
    ended_at: str | None
    error: str | None
