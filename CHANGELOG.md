# Changelog

## [1.1.0] – 2025-05-16

### Fixed
- Billing Limits: Fixed misconfigured `ACTOR_MAX_PAID_DATASET_ITEMS` handling by switching from manual environment variable parsing to Apify SDK's Actor.config.`max_paid_dataset_items` property for proper pay-per-result billing enforcement.

## [1.0.0] – 2025-05-16

### Added
- Initial release of the Phone Number Formatter Apify Actor.
- Bulk parsing, validation & formatting of phone numbers.
- Support for E.164, International, National & RFC3966 output formats.
- Default region specification (ISO 3166-1 alpha-2).
- Configurable batch size, concurrency, rate limiting, retries & backoff.
- Aggressive cleaning option for non-numeric characters.
- Example input/output JSON and CLI usage documentation.
