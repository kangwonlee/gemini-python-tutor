[![Build Status](https://github.com/kangwonlee/gemini-python-tutor/workflows/build/badge.svg)](https://github.com/kangwonlee/gemini-python-tutor/actions)
[![GitHub release](https://img.shields.io/github/release/kangwonlee/gemini-python-tutor.svg)](https://github.com/kangwonlee/gemini-python-tutor/releases)

# AI Python Code Tutor (Gemini)

Provide AI-powered feedback on Python code assignments using Google's Gemini language model.

## Key Features

* Provide feedback on Python code assignments.
* Support multiple JSON files by pytest-json-report plugin.
* Support multiple student files.

# Usage
* Please set `GOOGLE_API_KEY` in the repository's secrets.
``` yaml
  - name: AI Python Tutor
    uses: kangwonlee/gemini-python-tutor@v0.1.1
    if: always()
    with:
      # JSON files by pytest-json-report plugin
      report-files: report0.json, report1.json
      # python file including the student's code
      student-files: exercies.py
      # assignment instruction file
      readme-path: README.md
    env:
      GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
    timeout-minutes: 5
```
