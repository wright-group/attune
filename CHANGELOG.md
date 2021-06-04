# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Fixed
- Tune Test does not overwrite discrete tunes and runs instead of failing if they exist

## [0.4.2]

### Added
- discrete tunes which map ranges of outputs to string identifiers (suitable e.g. for yaq is-discrete trait implementation)

## [0.4.1]

### Changed
- setables are now fully optional

### Fixed
- Writing NDarrays to `instrument.json` files
- min and max value updating was buggy---now these values are never cached

## [0.4.0]

### Added
- initial release after a major rewrite

[Unreleased]: https://github.com/wright-group/attune/compare/0.4.2...master
[0.4.2]: https://github.com/wright-group/attune/compare/0.4.1...0.4.2
[0.4.1]: https://github.com/wright-group/attune/compare/0.4.0...0.4.1
[0.4.0]: https://github.com/wright-group/attune/releases/tag/0.4.0
