# -*- coding: utf-8 -*-
from typing import Callable
from urllib.parse import urlparse, ParseResult

import pandas as pd

from app.logger import logger
from app.exceptions.custom_http_exceptions import raise_HTTP_422


def df_converter(
    df: pd.DataFrame,
    field_name: str,
    converter: Callable
):
    """
    Converts a given field in data-frame
    based on the passed converter

    Parameters
    ----------
    df : pd.DataFrame
    field_name : str
    converter : Callable
        Converter must raise a Value Error
        So that it generates an automatic response to client

    Raises
    ------
    HTTPException
    """

    try:
        if field_name not in df.columns:
            raise ValueError(f"'{field_name}' Column is missing")
        df[field_name] = df[field_name].apply(converter)
    except ValueError as e:
        raise_HTTP_422(["File Fields"], str(e), "Validation Error")


def is_good_url(url: ParseResult) -> bool:
    """
    Checks if a url has any valid scheme (http/https)
    and a valid domain (google.com)

    Parameters
    ----------
    url : ParseResult

    Returns
    -------
    bool
    """

    if not url.scheme or not url.netloc:
        return False
    return True


def csv_urls_converter(csv_urls: str | None) -> list[ParseResult]:
    """
    Converter for commma separated urls(csv)
    By default raises erros if cannot be converted,
    which helps in validation

    Parameters
    ----------
    csv_urls : str

    Returns
    -------
    list[ParseResult]

    Raises
    ------
    ValueError
        - If datatype for csv_urls is not string
        - Or Cannot convert a string to valid URL
        - Or after spliting the string gets no URL, For eg. String of commas only
    """

    if not isinstance(csv_urls, str):
        err_string = f"Not comma separated urls: {csv_urls}"
        logger.error(err_string)
        raise ValueError(err_string)

    list_urls = [
        csv_url for csv_url in csv_urls.split(",") if csv_url
    ]

    if len(list_urls) == 0:
        err_string = f"No good url found: {csv_urls}"
        logger.error(err_string)
        raise ValueError(err_string)

    # Convets each URL using in-built urllib library for ease of validation
    for i, url in enumerate(list_urls):
        parsed_url = urlparse(url)

        if not is_good_url(parsed_url):
            err_string = f"Not valid url: {url}"
            logger.error(err_string)
            raise ValueError(err_string)

        list_urls[i] = parsed_url

    return list_urls
