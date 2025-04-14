from abc import ABCMeta
from threading import Lock
from typing import Dict

from PySide6.QtCore import QObject


class SingletonMeta(ABCMeta):
    """
    Thread-safe Singleton metaclass compatible with ABC.
    Ensures only one instance of a class exists across the app lifecycle.
    """
    __instances: Dict[type, object] = {}
    __lock: Lock = Lock()

    def __call__(cls, *args, **kwargs) -> object:
        with cls.__lock:
            if cls not in cls.__instances:
                instance = super().__call__(*args, **kwargs)
                cls.__instances[cls] = instance
        return cls.__instances[cls]


class MetaQObjectABC(type(QObject), ABCMeta):
    """Resolves metaclass conflicts between PySide6's QObject and Python's ABC."""
    pass
