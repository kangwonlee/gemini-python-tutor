# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - YYYY-MM-DD

### Added

- Added the ability to specify the Gemini model when using the AI Tutor GitHub Action.  A new `model` input has been added to the action, allowing users to select different Gemini models.  The default model remains `gemini-1.5-flash-latest` for backward compatibility.


### Changed


### Deprecated


### Removed


### Fixed


## [v0.1.6] - 2025-02-01

### Added
* MECE principle in comment generation
* if failed, assert the error message
* `fail-expected` argument to fail the test if the expected fail count not correct
* Add a feature to exclude common content of README.md assignment instruction.
    * Common content is marked by the starting marker ``From here is common to all assignments.`` and the ending marker ``Until here is common to all assignments.`` in the README.md file, surrounded by double backtick (ascii 96) characters.
* Add start and end markers to mutable code block in the prompt for Gemini.


### Changed
* Update license to BSD 3-Clause + Do Not Harm.
* Change the default value of `fail-expected` to `false`.
* Improve prompt for Gemini.
    * Add header and footer to the prompt.
    * Modify instruction for failed tests to "Please generate comments mutually exclusive and collectively exhaustive for the following failed test cases.".
    * Add start and end markers to mutable code block.


### Removed
* 'Currently Korean Only' from README.md.


## [v0.1.5] - 2024-10-20

### Added
* Swedish support

### Changed
* move README before pytest longrepr


## [v0.1.4] - 2024-10-09

### Added
* Bahasa Indonesia support
* Nederands support
* Vietnamese support


## [v0.1.3] - 2024-10-06

### Added
* Italian support


## [v0.1.2] - 2024-10-03

### Added
* API key as a required input.
* Future plans & more in README.md.
* International support


### Changed
* append integration step feedback output to the GITHUB_OUTPUT file of verification step.

### Removed
* environment variable 'GOOGLE_API_KEY'.

### Fixed
* integration test


## [0.1.1] - 2024-10-02

### Added
* Initially released

### Changed
* append integration step feedback output to the GITHUB_OUTPUT file of verification step.

### Fixed
* integration test


## [0.1.0] - 2024-10-02

### Added
* Initially released
