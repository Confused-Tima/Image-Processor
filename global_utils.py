import threading


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
