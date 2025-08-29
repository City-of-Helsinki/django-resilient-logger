import logging

from resilient_logger.sources import AbstractLogSource
from resilient_logger.targets import AbstractLogTarget


class ProxyLogTarget(AbstractLogTarget):
    """
    Logger target that sends the resilient log entries to another logger.
    """

    def __init__(self, name: str = __name__, required: bool = False) -> None:
        super().__init__(required)
        self._logger = logging.getLogger(name)

    def submit(self, entry: AbstractLogSource) -> bool:
        document = entry.get_document()
        audit_event = document["audit_event"]
        actor = audit_event.get("actor", "unknown")
        operation = audit_event.get("operation", "MANUAL")
        target = audit_event.get("target", "unknown")
        message: str = audit_event.pop("message")
        level = audit_event.get("level", logging.INFO)
        extra = audit_event.get("extra", {})

        context = {**extra, "actor": actor, "operation": operation, "target": target}
        self._logger.log(level=level, msg=message, extra=context)
        return True
