from abc import ABC, abstractmethod

from resilient_logger.sources import AbstractLogSource


class AbstractLogTarget(ABC):
    def __init__(self, required: bool = True):
        """
        Base class for logging targets.
        Required means if we can proceed even if the target fails.
        """
        self.required = required

    def is_required(self) -> bool:
        return self.required

    @abstractmethod
    def submit(self, entry: AbstractLogSource) -> bool:
        raise NotImplementedError()
