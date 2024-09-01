from fastapi import HTTPException


def raise_HTTP_422(loc: list, msg: str, err_type: str):
    raise HTTPException(
        status_code=422,
        detail=[{
            "loc": loc,
            "msg": msg,
            "type": err_type,
        }],
    )
