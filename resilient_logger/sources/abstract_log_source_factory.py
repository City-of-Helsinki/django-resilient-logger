from abc import ABC, abstractmethod

from resilient_logger.sources import AbstractLogSource


class AbstractLogSourceFactory(ABC):
    """
    Abstract base class (interface) that defines the method signatures.
    This is required because Django will not work if we import something
    that relies on Models too early.
    """

    @staticmethod
    @abstractmethod
    def create(**kwargs) -> type[AbstractLogSource]:
        raise NotImplementedError()
