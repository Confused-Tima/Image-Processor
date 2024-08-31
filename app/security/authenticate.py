# -*- coding: utf-8 -*-
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

from app.configs import settings

api_key_header = APIKeyHeader(name=settings.api_key_name, auto_error=False)


async def authenticate_api_key(
    api_key: str = Security(api_key_header)
) -> str:
    """
    Use this function to authenticate the API for api token in header

    Parameters
    ----------
    api_key : str, optional
        API key extracted from header, by default Security(api_key_header)

    Returns
    -------
    str
        API key

    Raises
    ------
    HTTPException
        403 Authentication Error
    """
    if settings.api_key:
        if api_key == settings.api_key:
            return api_key

        raise HTTPException(
            status_code=403,
            detail=[{
                "loc": [
                    settings.api_key_name,
                    api_key
                ],
                "msg": "Could not authenticate",
                "type": "Authentication Error"
            }]
        )
