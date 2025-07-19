# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - YYYY-MM-DD

### Added

### Changed

### Deprecated

### Removed

### Fixed

## [v0.3.6] - 2025-07-20


### Added
* Added logging info for the explanation language used in the entrypoint.

### Changed
* Upgraded the default Claude model from `claude-3-haiku-20240307` to `claude-sonnet-4-20250514`.
* Increased the maximum tokens for Claude API requests from 384 to 1024.
* Replaced the assertion for unexpected test failures with a `pass` statement (tests now proceed without failing the workflow on unexpected errors unless explicitly expected).
* Pinned dependencies: `pytest` to version 8.3.5 and `requests` to version 2.32.4

## [v0.3.3] - 2025-06-10


### Added
* Copyright registration info

### Changed
* bump `astral-sh/setup-uv` to @v6
* `requests` to 2.32.4

### Deprecated

### Removed

### Fixed

## [v0.3.1] - 2025-04-16

### Added

- **Multi-LLM Support**: Added support for Gemini, Grok, Nvidia NIM, Claude, and Perplexity via `llm_client.py` and `llm_configs.py`.
- **Command-Line Interface**: Introduced `main.py` for standalone feedback generation.
- **Pyproject.toml**: Added for dependency management with `pytest` and `requests`.
- **Testing Enhancements**: Included `test_llm_client.py` and `test_llm_configs.py` for unit testing LLM components.
- **Integration Testing**: Added xAI Grok API integration test in `build.yml`.
- Docker Hub badges for version and image size in `README.md`.
- Explicit `elif n_failed == 0: pass` in `entrypoint.py` for clarity.

### Changed

- **Refactored AI Tutor**: Replaced `ai_tutor.py` with `prompt.py` for modular prompt engineering.
- **Entrypoint Overhaul**: Updated `entrypoint.py` to support multiple LLMs, improved error handling, and added repository context.
- **Docker Configuration**: Updated `.dockerignore` and `Dockerfile` to reflect `prompt.py`.
- **GitHub Workflows**: Modified `build.yml` to use `uv` package manager and Python 3.11.
- **Testing Updates**: Renamed `test_ai_tutor.py` to `test_prompt.py` and updated tests for `prompt.py`. Adjusted `test_entrypoint.py` and `test_integration.py`.
- Reorganized `README.md` for better structure and streamlined "Troubleshooting".
- do not collect `longrepr` from skipped tests

### Deprecated


### Removed
- **Gemini-Specific Logic**: Removed from `ai_tutor.py`, replaced by generic LLM client.
- **Deprecated Dependencies**: Eliminated direct `pip` dependency management in favor of `uv` and `pyproject.toml`.

### Fixed
- **Error Handling**: Enhanced robustness in `entrypoint.py` and `llm_client.py` for file validation, API keys, and network errors.
- **Test Coverage**: Updated `test_entrypoint.py` to use `ValueError` instead of `AssertionError` for invalid paths.

## [v0.2.1] - 2025-03-08

### Added

* Add `workflow_dispatch` trigger to the Github Actions workflow.


### Removed
* Remove `GITHUB_OUTPUT` file writing.
* Remove raising an additional exception when `n_failed` is non zero.


## [v0.2.0] - 2025-03-08

### Added

* Write `feedback` to `$GITHUB_STEP_SUMMARY` if exists.
    This will show up under the Github Actions job graph.


## [v0.1.10] - 2025-02-26

### Changed
* Will include available `stderr` values when generating comments. Expected to be helpful sometimes.

## [v0.1.9] - 2025-02-22

### Changed
* for `edu-base` docker, write to `GITHUB_OUTPUT` only if the env var exists. If the script is running within the docker, there would be no `GITHUB_OUTPUT` enviroment variable.

## [v0.1.8] - 2025-02-20

### Added
* Manual publishing

### Removed
* no `pip` cache to save docker size
* support for linux/386,linux/arm/v7,linux/arm/v6 to save docker size
    Expected Github Actions runners : AMD64 or ARM64

## [v0.1.7] - 2025-02-18

### Added

- Added the ability to specify the Gemini model when using the AI Tutor GitHub Action.  A new `model` input has been added to the action, allowing users to select different Gemini models.  The default model remains `gemini-2.0-flash` for backward compatibility.
- Added Norwegian support
- Added Docker Image Build & Push to the CI/CD pipeline. Please use the following line
    ```yaml
      uses: docker://ghcr.io/github-id/action-name:tag
    ```

- Removed major version number yaml seemingly not working in the action.

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
