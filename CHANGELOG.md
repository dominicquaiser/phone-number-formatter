# Changelog

## [1.2.0] — 2025-09-05

### Added
- Dual Distribution Model: Now available as both an Apify actor and a standalone Python package
- Python Package Support: Full pip-installable package with proper setup.py and pyproject.toml
- CLI Tool: New console script phone-formatter for command-line usage
- Package Structure: Reorganized code into proper Python package structure under src/phone_number_formatter/
- Enhanced Documentation: Comprehensive README with installation and usage examples for all distribution methods
- Example Files: Added usage examples for basic operations and CSV processing

### Changed
- BREAKING: Restructured project layout - moved core logic to src/phone_number_formatter/core.py
- Enhanced: Updated README with comprehensive usage examples for all distribution methods
- Improved: Better separation between Apify actor functionality and standalone package code
- Updated: Documentation now covers installation via pip, usage as library, CLI tool, and Apify actor

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