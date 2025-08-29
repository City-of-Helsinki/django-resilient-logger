from importlib import reload

import resilient_logger.models as models
import resilient_logger.models.external_audit_log_entry as external_audit_log_entry
import resilient_logger.resilient_logger as resilient_logger
import resilient_logger.sources as sources
import resilient_logger.sources.external_audit_log_source as external_audit_log_source


def reload_models() -> None:
    reload(external_audit_log_entry)
    reload(models)

    reload(external_audit_log_source)
    reload(sources)

    reload(resilient_logger)
