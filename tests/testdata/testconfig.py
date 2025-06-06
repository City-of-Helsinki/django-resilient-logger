VALID_CONFIG_ALL_FIELDS = {
    "sources": [
        {
            "class": "resilient_logger.resilient_log_source.ResilientLogSource",
        }
    ],
    "targets": [
        {
            "class": "resilient_logger.proxy_log_target.ProxyLogTarget",
            "name": "proxy-target",
        }
    ],
    "batch_limit": 5000,
    "chunk_size": 500,
    "submit_unsent_entries": True,
    "clear_sent_entries": True,
}

VALID_CONFIG_MISSING_OPTIONAL = {
    "sources": [
        {
            "class": "resilient_logger.resilient_log_source.ResilientLogSource",
        }
    ],
    "targets": [
        {
            "class": "resilient_logger.proxy_log_target.ProxyLogTarget",
            "name": "proxy-target",
        }
    ],
}

INVALID_CONFIG_MISSING_TARGETS = {
    "sources": [
        {
            "class": "resilient_logger.resilient_log_source.ResilientLogSource",
        }
    ],
    "batch_limit": 5000,
    "chunk_size": 500,
    "submit_unsent_entries": True,
    "clear_sent_entries": True,
}

INVALID_CONFIG_MISSING_SOURCES = {
    "targets": [
        {
            "class": "resilient_logger.proxy_log_target.ProxyLogTarget",
            "name": "proxy-target",
        }
    ],
    "batch_limit": 5000,
    "chunk_size": 500,
    "submit_unsent_entries": True,
    "clear_sent_entries": True,
}
