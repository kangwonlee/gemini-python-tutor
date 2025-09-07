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

## [0.3.13] - 2025-09-07

### Added
- **Security Enhancements**:
  - Implemented `sanitize_input` function in `prompt.py` to prevent prompt injection attacks by removing or escaping common injection patterns and sensitive keywords (e.g., "ignore previous instructions", "grading logic").
  - Added input sanitization for student code, README content, and JSON reports to ensure safe inclusion in LLM prompts.
  - Introduced random delimiters to wrap content and prevent malicious prompt manipulation.
  - Added a `sleep 1` command in `build.yml` to stabilize pipeline execution by introducing a brief delay before running `entrypoint.py`.
  - Added guardrail instructions in `prompt.py` to restrict LLM behavior to providing feedback based solely on provided test results, student code, and assignment instructions.

### Changed
- **Build Workflow** (`build.yml`):
  - Reordered the model matrix to prioritize `claude-sonnet-4-20250514` and `google/gemma-2-9b-it`, ensuring consistency in model testing order.
  - Updated `actions/checkout` from `v4` to `v5` for improved performance and compatibility.
  - Changed default model from `gemini` to `gemini-2.5-flash` for improved performance and accuracy.
- **README** (`README.md`):
  - Updated project description to highlight enhanced security against prompt injection attacks.
  - Added details about new security features (input sanitization and random delimiters) in the "Key Features" and "Notes" sections.
  - Changed input parameters (`report-files`, `student-files`, `readme-path`) to have no default values, requiring explicit configuration for clarity.
  - Updated default model in input table and example workflow to `gemini-2.5-flash`.
  - Added note about prompt injection mitigation, emphasizing use in controlled environments.
  - Updated future enhancements to include advanced parsing for stronger prompt injection defenses.
  - Added troubleshooting guidance for prompt injection anomalies.
  - Updated acknowledgments to reflect contributions from `Gemini 2.5 Flash` instead of `Gemini 2.0 Flash`.
- **Prompt Logic** (`prompt.py`):
  - Applied input sanitization to `longrepr`, `stderr`, student code, README content, and locale files to prevent prompt injection.
  - Added guardrail instruction in `get_initial_instruction` to enforce strict adherence to feedback tasks.
  - Improved type hints and function signatures for better code clarity and maintainability.
  - Optimized string handling by replacing newlines with spaces and limiting input length to 10,000 characters to prevent prompt structure disruption.
- **Tests** (`test_prompt.py`):
  - Improved test assertions with descriptive error messages for better debugging.
  - Simplified test code by removing redundant tuple conversions and map operations.
  - Updated test fixtures and assertions to align with sanitized input handling.
  - Renamed test functions to follow a consistent naming convention (e.g., `test__exclude_common_contents__single` to `test_exclude_common_contents__single`).
  - Updated `expected_default_gemini_model` fixture to reflect the new default model `gemini-2.5-flash`.
  - Enhanced `test_collect_longrepr__compare_contents` to track found markers and report missing ones explicitly.
  - Corrected minor typos and formatting in test comments and strings (e.g., standardized language terms like "Foutmelding" for Dutch).

### Fixed
- Ensured consistent handling of README content by sanitizing inputs in `assignment_instruction` and `exclude_common_contents` to prevent malicious patterns from affecting prompt generation.
- Fixed potential issues in test suite by adding explicit type checking and non-empty string validation in `test_collect_longrepr__has_list_items_len`.
- Addressed missing marker detection in `test_collect_longrepr__compare_contents` by tracking found markers instead of modifying the marker list.

## [v0.3.12] - 2025-09-07

### Added
- Support for multiple LLM providers (Claude, Gemini, Grok, NVIDIA NIM, Perplexity) with dedicated configuration classes in `llm_configs.py`.
- `llm_client.py` for robust API interaction with retry, timeout, and error handling.
- Comprehensive integration tests in `build.yml` for multiple models (`gemini-2.5-flash`, `grok-code-fast`, `claude-sonnet-4-20250514`, `google/gemma-2-9b-it`, `sonar`) using both action and environment variable inputs.
- Model-to-provider mapping in `get_model_key_from_env()` to handle precise model IDs.

### Changed
- Updated `entrypoint.py` to support flexible model selection with fallback to `gemini-2.5-flash`.
- Modified `.dockerignore` and `Dockerfile` to include `llm_client.py` and `llm_configs.py`.
- Updated `action.yml` inputs: `report-files`, `student-files`, `readme-path` now required; `model` defaults to `gemini`; added `fail-expected`.
- Updated `GeminiConfig` default model to `gemini-2.5-flash` from `gemini-2.0-flash`.
- Updated `GrokConfig` default model to `grok-code-fast` from `grok-2-1212`.
- Enhanced `tests/test_entrypoint.py` to align with new fallback model (`gemini-2.5-flash`) and added test for `INPUT_API-KEY`.
- Improved logging checks in `tests/test_llm_client.py` for robustness.
- Added file markers in `tests/test_integration.py` and `tests/test_prompt.py`.

### Fixed
- Resolved 404 errors in integration tests for `google/gemma-2-9b-it` and `sonar` by adding model-to-provider mapping in `get_model_key_from_env()`.
- Fixed test failures in `test_get_model_key_from_env__fallback_gemini` and `test_get_model_key_from_env__no_model_fallback_gemini` by updating expected model to `gemini-2.5-flash`.

## [v0.3.7] - 2025-08-01

### Added
- **Flexible LLM Selection**: Added support for Claude, Grok, Nvidia NIM, and Perplexity alongside Gemini, with automatic fallback to Gemini or a single available API key if the specified model’s key is unavailable (`entrypoint.py`).
- **C/C++ Support**: Extended feedback capabilities to C/C++ assignments, using `pytest` and `pytest-json-report` to analyze compiled code (e.g., via `ctypes`) in a Docker environment (`README.md`).
- **Comprehensive Testing**: Added new test cases in `test_entrypoint.py` to cover single-key scenarios, Gemini fallback, empty key handling, and invalid model cases.

### Changed
- **Updated README**: Renamed to "AI Code Tutor" to reflect C/C++ and Python support. Clarified dependencies (`pytest==8.3.5`, `pytest-json-report==1.5.0`, `pytest-xdist==3.6.1`, `requests==2.32.4`) and API key setup with `INPUT_` prefix (e.g., `INPUT_GOOGLE_API_KEY`). Improved YAML example for GitHub Classroom with Docker-based C/C++ testing.
- **Enhanced Model Selection Logic**: Refactored `get_model_key_from_env` in `entrypoint.py` to handle missing `INPUT_MODEL`, prioritize specified model, and fall back to Gemini or single available key. Improved error messages for clarity.
- **Improved Error Handling**: Added `try-except` for writing to `GITHUB_STEP_SUMMARY` in `entrypoint.py` to handle permission issues in GitHub Actions.
- **Test Refinements**: Removed `mock_env_api_keys` fixture in `test_entrypoint.py` for better isolation, using `monkeypatch` directly. Updated tests to align with new model selection logic and `ValueError` exceptions.
- **Code Cleanup**: Streamlined `entrypoint.py` by removing redundant comments, improving type hints (e.g., `key: str` in `get_startwith`), and organizing `get_config_class` logic with a separate `get_config_class_dict`.

### Fixed
- **API Key Handling**: Fixed potential `KeyError` in `entrypoint.py` by using `os.getenv` with defaults, ensuring robust environment variable access.
- **Test Accuracy**: Corrected `test_get_model_key_from_env__invalid_model_no_gemini` to expect valid fallback to a single available key (e.g., Claude) instead of an error.

### Removed
- **Docker Badges**: Temporarily removed Docker Hub badges from `README.md` to align with updated deployment instructions (pending re-addition with verified image updates).

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
