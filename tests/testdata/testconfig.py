VALID_CONFIG_ALL_FIELDS = {
    "sources": [
        {
            "class": "resilient_logger.sources.ResilientLogSource",
        }
    ],
    "targets": [
        {
            "class": "resilient_logger.targets.ProxyLogTarget",
            "name": "proxy-target",
        }
    ],
    "batch_limit": 5000,
    "chunk_size": 500,
    "submit_unsent_entries": True,
    "clear_sent_entries": True,
    "environment": "dev",
    "origin": "test",
}

VALID_CONFIG_MISSING_OPTIONAL = {
    "sources": [
        {
            "class": "resilient_logger.sources.ResilientLogSource",
        }
    ],
    "targets": [
        {
            "class": "resilient_logger.targets.ProxyLogTarget",
            "name": "proxy-target",
        }
    ],
    "environment": "dev",
    "origin": "test",
}

INVALID_CONFIG_MISSING_TARGETS = {
    "sources": [
        {
            "class": "resilient_logger.sources.ResilientLogSource",
        }
    ],
    "batch_limit": 5000,
    "chunk_size": 500,
    "submit_unsent_entries": True,
    "clear_sent_entries": True,
    "environment": "dev",
    "origin": "test",
}

INVALID_CONFIG_EMPTY_TARGETS = {
    "sources": [
        {
            "class": "resilient_logger.sources.ResilientLogSource",
        }
    ],
    "targets": [],
    "batch_limit": 5000,
    "chunk_size": 500,
    "submit_unsent_entries": True,
    "clear_sent_entries": True,
    "environment": "dev",
    "origin": "test",
}

INVALID_CONFIG_MISSING_SOURCES = {
    "targets": [
        {
            "class": "resilient_logger.targets.ProxyLogTarget",
            "name": "proxy-target",
        }
    ],
    "batch_limit": 5000,
    "chunk_size": 500,
    "submit_unsent_entries": True,
    "clear_sent_entries": True,
    "environment": "dev",
    "origin": "test",
}

INVALID_CONFIG_EMPTY_SOURCES = {
    "sources": [],
    "targets": [
        {
            "class": "resilient_logger.targets.ProxyLogTarget",
            "name": "proxy-target",
        }
    ],
    "batch_limit": 5000,
    "chunk_size": 500,
    "submit_unsent_entries": True,
    "clear_sent_entries": True,
    "environment": "dev",
    "origin": "test",
}

INVALID_CONFIG_MISSING_ENVIRONMENT = {
    "targets": [
        {
            "class": "resilient_logger.targets.ProxyLogTarget",
            "name": "proxy-target",
        }
    ],
    "batch_limit": 5000,
    "chunk_size": 500,
    "submit_unsent_entries": True,
    "clear_sent_entries": True,
    "origin": "test",
}

INVALID_CONFIG_EMPTY_ENVIRONMENT = {
    "targets": [
        {
            "class": "resilient_logger.targets.ProxyLogTarget",
            "name": "proxy-target",
        }
    ],
    "batch_limit": 5000,
    "chunk_size": 500,
    "submit_unsent_entries": True,
    "clear_sent_entries": True,
    "environment": "",
    "origin": "test",
}

INVALID_CONFIG_MISSING_ORIGIN = {
    "targets": [
        {
            "class": "resilient_logger.targets.ProxyLogTarget",
            "name": "proxy-target",
        }
    ],
    "batch_limit": 5000,
    "chunk_size": 500,
    "submit_unsent_entries": True,
    "clear_sent_entries": True,
    "environment": "dev",
}

INVALID_CONFIG_EMPTY_ORIGIN = {
    "targets": [
        {
            "class": "resilient_logger.targets.ProxyLogTarget",
            "name": "proxy-target",
        }
    ],
    "batch_limit": 5000,
    "chunk_size": 500,
    "submit_unsent_entries": True,
    "clear_sent_entries": True,
    "environment": "dev",
    "origin": "",
}
