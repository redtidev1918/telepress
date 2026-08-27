# Changelog

All notable changes to TelePress are documented in this file. The project uses
[Semantic Versioning](https://semver.org/) and the changelog is maintained by
Release Please from Conventional Commits.

## [0.4.0](https://github.com/redtidev1918/telepress/compare/v0.3.5...v0.4.0) (2026-08-27)


### Features

* defer image host initialization until first upload use ([44445e1](https://github.com/redtidev1918/telepress/commit/44445e1784a513fc0811b9d73e9937a30f12871c))
* keep API server blocking work off the event loop ([ee43828](https://github.com/redtidev1918/telepress/commit/ee43828fdda29e49f663a87d9abdd7e3c897eb5b))


### Bug Fixes

* block zip-slip sibling paths and harden compression search ([d5d4661](https://github.com/redtidev1918/telepress/commit/d5d4661d119fab9a516d3bae7796685dc0b8f806))
* raise a clear error when telepress-server lacks the api extra ([08b6fac](https://github.com/redtidev1918/telepress/commit/08b6facf3d0acb6a4cb6e29d4038d5bfa105006a))


### Documentation

* rewrite READMEs and add contribution and release guides ([b433122](https://github.com/redtidev1918/telepress/commit/b4331220f8868acc215f2680f7fd547998b831bc))

## [0.3.5] - 2025-12-09

### Added

- Added `--api-url` support for Telegraph-compatible API endpoints.

### Changed

- Made image-upload worker count configurable.
- Improved external image-host configuration and documentation.

## [0.3.0] - 2025-12-08

### Added

- Added Rclone batch uploads and S3-compatible storage support.
- Added automatic image compression and concurrent batch uploads.
- Added plain-text chapter detection and automatic pagination.
- Added configuration checks, progress output, and comprehensive tests.

## [0.1.0] - 2025-12-07

### Added

- Initial Markdown and plain-text publishing support for Telegraph.
