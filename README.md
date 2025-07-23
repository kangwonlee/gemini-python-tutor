[![Build Status](https://github.com/kangwonlee/gemini-python-tutor/workflows/build/badge.svg)](https://github.com/kangwonlee/gemini-python-tutor/actions)
[![GitHub release](https://img.shields.io/github/release/kangwonlee/gemini-python-tutor.svg)](https://github.com/kangwonlee/gemini-python-tutor/releases)
[![Docker Image Version (latest by date)](https://img.shields.io/docker/v/beachgoer/gemini-python-tutor?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/beachgoer/gemini-python-tutor)
[![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/beachgoer/gemini-python-tutor?logo=docker)](https://hub.docker.com/r/beachgoer/gemini-python-tutor)

# AI Python Code Tutor

This GitHub Action leverages AI to analyze test results and Python code, delivering personalized feedback for student assignments. It identifies errors, suggests improvements, and explains concepts clearly.

The AI tutor detects logic errors, recommends efficient algorithms, simplifies complex topics, and links to relevant documentation. It saves instructors time, ensures consistent feedback, and empowers students to learn anytime, anywhere.

## Key Features

- AI-powered feedback for Python code assignments.
- Supports multiple JSON test report files from `pytest-json-report`.
- Analyzes multiple student code files.
- Customizable explanation language (e.g., English, Korean).
- Excludes common README content to optimize API usage.

## Prerequisites

To use this action, you’ll need:

- **pytest-json-report plugin**: Generates JSON test reports for analysis.
  - Install it with:
    ```bash
    pip install pytest-json-report
    ```
  - Generate a JSON report with:
    ```bash
    python -m pytest --json-report --json-indent=4 --json-report-file=report.json tests/test_my_test_file.py
    ```
  - See [pytest-json-report documentation](https://pypi.org/project/pytest-json-report/).

- **Google API Key**: Set as `GOOGLE_API_KEY` in your repository secrets.

## Usage

1. Add a workflow file (e.g., `.github/workflows/classroom.yml`) to your repository.
2. Configure it as follows:

``` yaml
on: [push]

jobs:
  grade:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: pip install pytest pytest-json-report
      - name: Run tests
        run: |
          python -m pytest --json-report --json-report-file=report.json tests/test_my_test_file.py
      - name: AI Python Tutor
        uses: kangwonlee/gemini-python-tutor@v0.2.1
        if: always()  # Runs even if, or especially when, tests fail
        with:
          report-files: report.json
          api-key: ${{ secrets.GOOGLE_API_KEY }}
          student-files: exercise.py
          readme-path: README.md
          explanation-in: English
        timeout-minutes: 5
```

### Notes
- The action processes JSON output from `pytest-json-report` to evaluate test results and provide feedback.
- To save API usage, exclude common README content by marking it with:
  - Start: ``From here is common to all assignments.``
  - End: ``Until here is common to all assignments.``
  - Use double backticks (``) around these markers.

### Optimizing pytest for LLMs
- Use descriptive test names (e.g., `test_calculate_sum_correctly`).
- Add clear assertion messages (e.g., `assert x == 5, "Expected 5, got {x}"`).
- Keep tests simple and focused for better AI interpretation.

## Inputs

| Input             | Description                                      | Required | Default         |
|-------------------|--------------------------------------------------|----------|-----------------|
| `report-files`    | Comma-separated list of JSON report files        | Yes      | `report.json`   |
| `api-key`         | Google API key for Gemini                        | Yes      | N/A             |
| `student-files`   | Comma-separated list of student Python files     | Yes      | `exercise.py`   |
| `readme-path`     | Path to assignment instructions (README.md)      | No       | `README.md`     |
| `explanation-in`  | Language for feedback (e.g., English, Korean)    | No       | `English`       |
| `model`           | Gemini model (e.g., `gemini-2.0-flash`)          | No       | `gemini-2.0-flash` |


### Example with Multiple Files

``` yaml
with:
  report-files: 'report1.json, report2.json, reports/*.json'
  api-key: ${{ secrets.GOOGLE_API_KEY }}
  student-files: 'exercise1.py, exercise2.py'
  readme-path: README.md
  explanation-in: English
```

## Outputs

- **Feedback**: Written to `$GITHUB_STEP_SUMMARY` (if set) in Markdown format, visible in the GitHub Job Summary.

## Limitations

- Developed primarily to support Python code assignments.
- Requires `pytest-json-report` for test reports.

## Future Enhancements

- Expand natural language support with auto-detection.
- Add options for AI models (e.g., Gemini Advanced, Grok, Perplexity).
- Facilitate supporting more programming languages.
- Include a `verbose` mode for detailed feedback.

## Troubleshooting

Check the action logs in the GitHub Actions tab for details.

### Common Errors
- **API Key Issues**:
  - "Invalid API key": Verify `GOOGLE_API_KEY` in secrets.
- **Report File Issues**:
  - "Report file not found": Ensure JSON report exists.
- **Student File Issues**:
  - "Student file not found": Check file paths and `.py` extensions.

### Debugging Tips
- View logs in the "AI Python Tutor" job.
- Test locally with [act](https://github.com/nektos/act).
- Environment variable `INPUT_FAIL-EXPECTED` available for testing and debugging

## Contact

Questions? Please contact [https://github.com/kangwonlee](https://github.com/kangwonlee).

## License

BSD 3-Clause License + Do Not Harm.
Copyright (c) 2024 Kangwon Lee

## Acknowledgements

* Built using [python-github-action-template](https://github.com/cicirello/python-github-action-template) by Vincent A. Cicirello (MIT License).
* Gemini 2.0 Flash and Grok 3 helped with the code and documentation.
* Registered as #C-2024-034203, #C-2024-035473, #C-2025-016393, and #C-2025-027967 with the Korea Copyright Commission.
