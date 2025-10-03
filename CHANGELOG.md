# CHANGELOG

All notable project-wide changes will be documented in this file. Note that each subproject has its own CHANGELOG.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and [Commons Changelog](https://common-changelog.org). This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Types of Changes

- Added: for new features.
- Changed: for changes in existing functionality.
- Deprecated: for soon-to-be removed features.
- Removed: for now removed features.
- Fixed: for any bug fixes.
- Security: in case of vulnerabilities.

---

## [0.1.1] - 2025-10-03

### Added
- FastAPI application (`pmo.api`) with SQLAdmin dashboard, REST endpoints, and sample-data seeding endpoint.
- CLI `serve` command (`pmo.cli serve`) to launch the admin server with optional fixtures and reload support.
- Bun/Vite-based PWA (`apps/pwa/`) delivering role-specific dashboards for project, finance, and general managers.
- Shared database utilities (`pmo.db`) and reusable sample data loader for tests, API seeding, and CLI operations.
- Test coverage for the new API (`tests/test_api.py`).

### Changed
- Documentation overhauled with comprehensive README and contributor guidance updates.
- `.gitignore` hardened to exclude PWA artifacts, binaries, and sensitive files.

### Fixed
- Graph generation no longer attempts to open GUI viewers in tests/headless environments.

### Security
- Ensured sample data seeding is idempotent and sanitised, reducing accidental duplicate inserts.

## [0.1.x]



## [0.1.0] - Initial Release

- Project created
