# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Fixed
- Fixed bug where `DiscreteTune`s returned only one value when called (regardless of input shape) 

## [0.4.4]

### Fixed
- Units on attune.intensity are set according to the axis they are referencing
- Resolve some issues discovered by CodeQL which could result in unexpected behavior

### Added
- `update_merge` function which allows applying tunes from one instrument into an existing instrument.

## [0.4.3]

### Added
- Reading Topas4 formatted curves (from a directory of JSON files)
- Setables now have the ability to have defaults, which are added to Notes if not otherwise specified.
- Add transition to rename an Instrument

### Fixed
- Tune Test does not overwrite discrete tunes and runs instead of failing if they exist

## [0.4.2]

### Added
- discrete tunes which map ranges of outputs to string identifiers (suitable e.g. for yaq is-discrete trait implementation)
- Allow tunes to override setables from referenced arrangements (e.g. if idl refers to sig and idl also has setables that are defined in sig, use those defined in idl)

## [0.4.1]

### Added
- from_topas4  and associated test script, for import of Topas4 file format 

### Changed
- setables are now fully optional

### Fixed
- Writing NDarrays to `instrument.json` files
- min and max value updating was buggy---now these values are never cached

## [0.4.0]

### Added
- initial release after a major rewrite

[Unreleased]: https://github.com/wright-group/attune/compare/0.4.4...master
[0.4.4]: https://github.com/wright-group/attune/compare/0.4.3...0.4.4
[0.4.3]: https://github.com/wright-group/attune/compare/0.4.2...0.4.3
[0.4.2]: https://github.com/wright-group/attune/compare/0.4.1...0.4.2
[0.4.1]: https://github.com/wright-group/attune/compare/0.4.0...0.4.1
[0.4.0]: https://github.com/wright-group/attune/releases/tag/0.4.0
