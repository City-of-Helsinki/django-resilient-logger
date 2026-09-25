<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Logger that ensures that logs sent out to external service.](#logger-that-ensures-that-logs-sent-out-to-external-service)
  - [Adding django-resilient-logger to your Django project](#adding-django-resilient-logger-to-your-django-project)
    - [Adding django-resilient-logger to Django apps](#adding-django-resilient-logger-to-django-apps)
    - [Configuring django-resilient-logger](#configuring-django-resilient-logger)
- [Workarounds](#workarounds)
  - [django-auditlog Patching](#django-auditlog-patching)
    - [Configuration Settings](#configuration-settings)
    - [Manual or Custom Usage](#manual-or-custom-usage)
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
        {"class": "resilient_logger.sources.ResilientLogSource"},
        {"class": "resilient_logger.sources.DjangoAuditLogSource"},
    ],
    "targets": [
        {
            "class": "resilient_logger.targets.ElasticsearchLogTarget",
            "es_url": env("AUDIT_LOG_ES_URL"),
            "es_username": env("AUDIT_LOG_ES_USERNAME"),
            "es_password": env("AUDIT_LOG_ES_PASSWORD"),
            "es_index": env("AUDIT_LOG_ES_INDEX"),
            "es_compress": False,
            "required": True,
        }
    ],
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
# Workarounds

`django-resilient-logger` includes built-in workarounds to resolve structural and privacy issues when integrating with third-party libraries.

## django-auditlog Patching

By default, `django-auditlog` uses `smart_str` (which invokes standard `__str__` methods) to populate the `object_repr` field on `LogEntry` records. Because `__str__` representations in models often contain sensitive personal data (e.g., names, email addresses, phone numbers), this default behavior can lead to unintentional **Personally Identifiable Information (PII) leakage** in audit logs.

The `DjangoAuditLogEntryManager` workaround intercepts log entry creation (`log_create` and `log_m2m_changes`) by temporarily monkey-patching `auditlog.models.smart_str` and replacing `LogEntry.objects` (and its associated manager references `base_manager` and `default_manager`) with a custom manager.

### Configuration Settings

You can enable and configure the PII-safe representation function directly in `settings.py`:

```python
# Enable/disable the django-auditlog monkey patch (Defaults to False)
RESILIENT_LOGGER_PATCH_DJANGO_AUDITLOG = True

# Custom string representation callback to sanitize or replace PII (Defaults to None)
# Accepts a dotted import path string, callable function, or None (uses default resolver)
RESILIENT_LOGGER_DJANGO_AUDITLOG_REPR_FN = "my_project.utils.pii_safe_object_repr"
```

- **RESILIENT_LOGGER_PATCH_DJANGO_AUDITLOG**: Boolean flag. When set to `True`, `resilient_logger` automatically applies the manager patch during Django startup (`AppConfig.ready()`).
- **RESILIENT_LOGGER_DJANGO_AUDITLOG_REPR_FN**:
  - `None` (or omitted): Uses the built-in resolver, which strips sensitive field data and represents Django models formatted strictly as `ModelName (PK)` (e.g., `User (42)`). **Note**: If the primary key itself contains PII (such as an email address), the built-in resolver will not redact it.
  - Dotted string path (e.g., `"path.to.module.custom_fn"`): Resolves and executes the specified custom representation callable.
  - Callable: Direct function handle (when configuring programmatically).

### Manual or Custom Usage

If you need to trigger or control the patch programmatically (e.g., within isolated test cases or scripts), call `DjangoAuditLogEntryManager.patch()` directly.

The `patch()` static method returns a `restore()` function to safely revert `LogEntry` managers to their unpatched state:

```python
from resilient_logger.workarounds.models import DjangoAuditLogEntryManager

# 1. Apply patch with a custom PII-sanitizing function or default fallback (ModelName (PK))
restore_patch = DjangoAuditLogEntryManager.patch(object_repr_fn=pii_safe_repr_fn)

try:
    # Perform operations triggering django-auditlog...
    pass
finally:
    # 2. Revert LogEntry managers back to original state
    restore_patch()
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
pip install -e ".[all]"
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
