# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Added do not retry handling for error codes 4xx
- endpoint.py no longer retries on all raised errors this is defined by adding the giveup argument and is defined in retry.py
- Added 3 tests to validate expected backoff behavior. 11 tests total due to parameterization
- Changed Backoff behavior
  - Change on_exception mode to constant to have the same duration on each retry 
  - Added on_predicate to retry for the duration read from header Retry-After for error code 429 & 503
- All errors that should be retried returns true

### Added
### Changed
 - Use BAT2

## 0.0.2
### Added
- Exceptions raised in `get_data` now provides `response`, so the raw
  response may be inspected.
- Added the `format_payload` option to `get_data`.
## 0.0.1

### Added
- Added a base class for interacting with DUPLA
- Added functionality for json web token authentication
