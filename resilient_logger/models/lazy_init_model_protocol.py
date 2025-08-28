from typing import Protocol


class LazyInitModelProtocol(Protocol):
    """
    Protocol for models that requires lazy init
    """

    _initialized: bool

    @classmethod
    def init_model(cls) -> bool:
        return False
