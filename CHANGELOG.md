# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Changed retry-behaviour:
  - Only perform retry for the following errors:
    - Http error 429 (Too many requests)
    - Http error 503 (Service unavailable)
    - `requests.exceptions.ConnectionError`
    - `requests.exceptions.Timeout`
  - For the 429 and 503, the `Retry-After` header (if present) is respected.
  - Do *not* perform retry on `DuplaResponseException` (which is an internal Exception, signifying invalid data returned from server).

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
