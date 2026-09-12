# Changelog

All notable changes to TelePress are documented in this file. The project uses
[Semantic Versioning](https://semver.org/) and the changelog is maintained by
Release Please from Conventional Commits.

## [0.6.2](https://github.com/redtidev1918/telepress/compare/v0.6.1...v0.6.2) (2026-09-12)


### Documentation

* 中文设为默认语言，统一双语命名与侧边栏，补齐下载页与英文文档 ([#20](https://github.com/redtidev1918/telepress/issues/20)) ([8221934](https://github.com/redtidev1918/telepress/commit/82219346f9aebe08f5edac0d20573b619bb80570))
* 显式声明 CDN 壳站点的导航例外 ([#22](https://github.com/redtidev1918/telepress/issues/22)) ([16617e9](https://github.com/redtidev1918/telepress/commit/16617e9a2d0b8f263a12f327059c3e994ff6fb86))
* 英文发版文档中的中文句子改为英文 ([74e9a59](https://github.com/redtidev1918/telepress/commit/74e9a59c31bc0df0f085feb85c206116401f2f21))

## [0.6.1](https://github.com/redtidev1918/telepress/compare/v0.6.0...v0.6.1) (2026-09-08)


### Documentation

* publish documentation site ([c5a88a6](https://github.com/redtidev1918/telepress/commit/c5a88a6f6ff4d05f2e2a3ff83af666d34af7ec97))

## [0.6.0](https://github.com/redtidev1918/telepress/compare/v0.5.0...v0.6.0) (2026-09-07)


### Features

* **server:** /publish/* 可选请求级 API key 鉴权（Bearer / X-TelePress-Key） ([4078e61](https://github.com/redtidev1918/telepress/commit/4078e613cc43a8d66eab2aece848b28415939af1))

## [0.5.0](https://github.com/redtidev1918/telepress/compare/v0.4.0...v0.5.0) (2026-08-30)


### Features

* **core:** support optional footer nodes in gallery publishing ([4efcf12](https://github.com/redtidev1918/telepress/commit/4efcf12df60a9fdb49ebb6e104fe28d3eddb6aca))
* **server:** add /publish/gallery endpoint for multi-image galleries ([545e0fb](https://github.com/redtidev1918/telepress/commit/545e0fbe08413e84a5a33f5629078e96f7722675))


### Documentation

* document /publish/gallery REST endpoint ([cd03d83](https://github.com/redtidev1918/telepress/commit/cd03d83d0883a0dd671cd9352d70b3ba320f43d2))

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
