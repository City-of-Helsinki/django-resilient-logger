<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Logger that ensures that logs sent out to external service.](#logger-that-ensures-that-logs-sent-out-to-external-service)
  - [Adding django-resilient-logger to your Django project](#adding-django-resilient-logger-to-your-django-project)
    - [Adding django-resilient-logger to Django apps](#adding-django-resilient-logger-to-django-apps)
    - [Configuring django-resilient-logger](#configuring-django-resilient-logger)
- [Development](#development)
  - [Running tests](#running-tests)
  - [Code format](#code-format)
  - [Commit message format](#commit-message-format)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Logger that ensures that logs sent out to external service.

`django-resilient-logger` is a logger module that stores logs in local DB and synchronizes those with external log target.
If for some reason synchronization to external service does not work at the given time, it will retry it at later time.
Management tasks require an external cron trigger.

Cron triggers are designed to be run in following schedule:
- `submit_unsent_entries` once in every 15 minutes.
- `clear_sent_entries` once a month.

To manually trigger the scheduled tasks, one can run commands:
```bash
python ./manage.py submit_unsent_entries
python ./manage.py clear_sent_entries
```

## Adding django-resilient-logger to your Django project

Add `django-resilient-logger` in your project"s dependencies.

### Adding django-resilient-logger to Django apps

To install this logger, append `resilient_logger` to `INSTALLED_APPS` in settings.py:

```python
INSTALLED_APPS = (
    "resilient_logger"
    ...
)
```

### Configuring django-resilient-logger

To configure resilient logger, you must provide config section in your settings.py.

Configuration must contain required `origin`, `environment`, `sources` and `targets` keys. It also accepts optional keys `batch_limit`, `chunk_size`, `clear_sent_entries` and `submit_unsent_entries`.
- `origin` is the name of the application or unique identifier of it.
- `environment` is the name of the environment where the application is running.
- `sources` expects array of objects with property `class` (full class path) being present. Other properties are ignored.
- `targets` expects array of objects with `class` (full class path) and being present. Others are passed as constructor parameters.

```python
RESILIENT_LOGGER = {
    "origin": "NameOfTheApplication",
    "environment": env("AUDIT_LOG_ENV"),
    "sources": [
        { "class": "resilient_logger.sources.ResilientLogSource" },
        { "class": "resilient_logger.sources.DjangoAuditLogSource" },
    ],
    "targets": [{
        "class": "resilient_logger.targets.ElasticsearchLogTarget",
        "es_url": env("AUDIT_LOG_ES_URL"),
        "es_username": env("AUDIT_LOG_ES_USERNAME"),
        "es_password": env("AUDIT_LOG_ES_PASSWORD"),
        "es_index": env("AUDIT_LOG_ES_INDEX"),
        "required": True
    }],
    "batch_limit": 5000,
    "chunk_size": 500,
    "submit_unsent_entries": True,
    "clear_sent_entries": True,
}
```

In addition to the django-resilient-logger specific configuration, one must also configure logger handler to actually use it.
In the sample below the configured logger is called `resilient` and it will use the `RESILIENT_LOGGER` configuration above:
```python
LOGGING = {
    "handlers": {
        "resilient": {
            "class": "resilient_logger.handlers.ResilientLogHandler",
            ...
        }
        ...
    },
    "loggers": {
        "": {
            "handlers": ["resilient"],
            ...
        },
    ...
    }
}
```

# Development

Virtual Python environment can be used. For example:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install package requirements:

```bash
pip install -e .
```

Install development requirements:

```bash
pip install -r requirements-test.txt
```

## Running tests

```bash
pytest
```

## Code format

This project uses [Ruff](https://docs.astral.sh/ruff/) for code formatting and quality checking.

Basic `ruff` commands:

* lint: `ruff check`
* apply safe lint fixes: `ruff check --fix`
* check formatting: `ruff format --check`
* format: `ruff format`

[`pre-commit`](https://pre-commit.com/) can be used to install and
run all the formatting tools as git hooks automatically before a
commit.


## Commit message format

New commit messages must adhere to the [Conventional Commits](https://www.conventionalcommits.org/)
specification, and line length is limited to 72 characters.

When [`pre-commit`](https://pre-commit.com/) is in use, [`commitlint`](https://github.com/conventional-changelog/commitlint)
checks new commit messages for the correct format.
