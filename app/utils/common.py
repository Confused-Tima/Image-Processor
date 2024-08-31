# -*- coding: utf-8 -*-
import threading

from pydantic import ValidationError, BaseModel

from app.logger import logger


def validate_object(obj: dict, model: BaseModel) -> BaseModel | None:
    """
    Validates the give object against a given pydantic model.

    Parameters
    ----------
    obj : dict
    model : BaseModel

    Returns
    -------
    BaseModel | None
    """
    try:
        validated_object = model(**obj)
    except ValidationError as e:
        logger.error(f"Error while validating: {obj} - {e}")
        return None

    return validated_object


class SingletonMeta(type):
    """Meta class to create other singleton classes"""
    __instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            with cls._lock:
                if cls not in cls.__instances:
                    cls.__instances[cls] = super(
                        SingletonMeta,
                        cls
                    ).__call__(*args, **kwargs)

        return cls.__instances[cls]
