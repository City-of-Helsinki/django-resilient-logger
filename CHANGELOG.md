<!-- DOCTOC SKIP -->
# Changelog

## [3.0.0](https://github.com/City-of-Helsinki/django-resilient-logger/compare/v2.3.0...v3.0.0) (2026-09-08)


### ⚠ BREAKING CHANGES

* simplify django-auditlog's message content ([#53](https://github.com/City-of-Helsinki/django-resilient-logger/issues/53))

### Features

* Add django-logger-extra as optional dep ([#52](https://github.com/City-of-Helsinki/django-resilient-logger/issues/52)) ([a3dc5e6](https://github.com/City-of-Helsinki/django-resilient-logger/commit/a3dc5e6386d8ba5a0176d84a7ea2dc08db1a0460))
* Simplify django-auditlog's message content ([#53](https://github.com/City-of-Helsinki/django-resilient-logger/issues/53)) ([b793ec0](https://github.com/City-of-Helsinki/django-resilient-logger/commit/b793ec0a115ece60ac54e45d93c16f04b9945bdd))

## [2.3.0](https://github.com/City-of-Helsinki/django-resilient-logger/compare/v2.2.0...v2.3.0) (2026-05-27)


### Features

* Add too big payload handling ([#46](https://github.com/City-of-Helsinki/django-resilient-logger/issues/46)) ([21a55d8](https://github.com/City-of-Helsinki/django-resilient-logger/commit/21a55d899252bfb2557c5fd967e41d2c217764e2))

## [2.2.0](https://github.com/City-of-Helsinki/django-resilient-logger/compare/v2.1.1...v2.2.0) (2026-05-19)


### Features

* Split log source into repository and entry ([#43](https://github.com/City-of-Helsinki/django-resilient-logger/issues/43)) ([e4d8a67](https://github.com/City-of-Helsinki/django-resilient-logger/commit/e4d8a67f5c96e904b517332cb1cccb1e98768735))


### Bug Fixes

* Fallback changes_str for m2o and m2m entries ([#45](https://github.com/City-of-Helsinki/django-resilient-logger/issues/45)) ([e67a696](https://github.com/City-of-Helsinki/django-resilient-logger/commit/e67a6967286586c79ad75f004ffa6110454859a5))

## [2.1.1](https://github.com/City-of-Helsinki/django-resilient-logger/compare/v2.1.0...v2.1.1) (2026-04-13)


### Dependencies

* Drop support for django 4.2, 5.1, add 6.0 support ([a83d568](https://github.com/City-of-Helsinki/django-resilient-logger/commit/a83d568521964d4aa0ff151d585ae2cee5dc3b22))

## [2.1.0](https://github.com/City-of-Helsinki/django-resilient-logger/compare/v2.0.0...v2.1.0) (2026-02-17)


### Features

* Fallback changes_str for django-auditlog ([f175ab4](https://github.com/City-of-Helsinki/django-resilient-logger/commit/f175ab45a540b9452dfc5fa1caacef99a808a1c0))


### Bug Fixes

* Access operation and objects with getters ([5aef92e](https://github.com/City-of-Helsinki/django-resilient-logger/commit/5aef92e5c7a01a8556047c5ba1e0f64c13fa1897))

## [2.0.0](https://github.com/City-of-Helsinki/django-resilient-logger/compare/v1.2.0...v2.0.0) (2026-02-11)


### ⚠ BREAKING CHANGES

* Tasks that previously ran by default are now disabled. If some project relied on default values, those configurations must be updated to enable the cron tasks explicitly.

### Features

* Add better config validations ([a6afd1f](https://github.com/City-of-Helsinki/django-resilient-logger/commit/a6afd1fe8a3667149bc33d54b42fd4f3ac36edd4))
* Change default task enabled states ([98ceb4f](https://github.com/City-of-Helsinki/django-resilient-logger/commit/98ceb4fac7c5bd7896f95a5d561fd084d4205e51))

## [1.2.0](https://github.com/City-of-Helsinki/django-resilient-logger/compare/v1.1.1...v1.2.0) (2025-12-16)


### Features

* Use elasticsearch8 as a requirement ([ba65a8a](https://github.com/City-of-Helsinki/django-resilient-logger/commit/ba65a8a80aaf67736109886bcb6b627bef65f051))

## [1.1.1](https://github.com/City-of-Helsinki/django-resilient-logger/compare/v1.1.0...v1.1.1) (2025-11-28)


### Bug Fixes

* Add missing super calls ([be3dc29](https://github.com/City-of-Helsinki/django-resilient-logger/commit/be3dc2973659515762329e107a30ccbdc6c5779b))

## [1.1.0](https://github.com/City-of-Helsinki/django-resilient-logger/compare/v1.0.0...v1.1.0) (2025-11-25)


### Features

* Support bulk create for ResilientLogSource ([aeab1d9](https://github.com/City-of-Helsinki/django-resilient-logger/commit/aeab1d930cad52ac35056920ec4f947acfd079ad))


### Bug Fixes

* **readme:** Update instructions for development requirements ([173c521](https://github.com/City-of-Helsinki/django-resilient-logger/commit/173c521a44104353e5faebac6564d4aef8f3ee90))

## [1.0.0](https://github.com/City-of-Helsinki/django-resilient-logger/compare/v0.3.7...v1.0.0) (2025-11-12)


### Features

* Add source_pk as audit event extra ([425c621](https://github.com/City-of-Helsinki/django-resilient-logger/commit/425c621b9aae00155e85ec23ecdeb988884a904d))


### Dependencies

* Update python and django version support ([f7fe1af](https://github.com/City-of-Helsinki/django-resilient-logger/commit/f7fe1afe65e16020a83d401cb6eeb2a8e04033fc))


### Documentation

* Update README to include AUDIT_LOG_ENV ([7ae721a](https://github.com/City-of-Helsinki/django-resilient-logger/commit/7ae721a26e44378490213fd4f161857c9278ebcf))
