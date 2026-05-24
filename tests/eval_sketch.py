#!/usr/bin/env python3
"""Feedback-quality eval — SKETCH ONLY (2026-05-24).

This is the minimal seed described in REFACTOR-PLAN-2026-05-24.md, not a real
eval. It deliberately does NOT call any LLM: it asserts on the *prompt that
would be sent* (the part the prompt refactor controls) against a per-case
rubric. The TODO markers show where reply-scoring (LLM-judge or keyword check
on the model's answer) plugs in once an API budget is allocated.

Run manually:  python tests/eval_sketch.py
It is intentionally kept out of the per-PR test path.
"""

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # import prompt / prompt_policy

import prompt  # noqa: E402


def check_rubric(name, text, must_contain=(), must_not_contain=()):
    problems = []
    low = text.lower()
    for needle in must_contain:
        if needle.lower() not in low:
            problems.append(f"MISSING expected substring: {needle!r}")
    for needle in must_not_contain:
        if needle.lower() in low:
            problems.append(f"PRESENT forbidden substring: {needle!r}")
    status = "PASS" if not problems else "FAIL"
    print(f"[{status}] {name}")
    for p in problems:
        print(f"        - {p}")
    return not problems


# --- Case 1: all tests passed -------------------------------------------------
# The "all-passed" report fixture would normally come from a real pytest run;
# here we hand-build a trivial all-passed report so the sketch is self-contained.
def case_all_passed():
    report = HERE / "_eval_all_passed.json"
    report.write_text('{"tests": [{"outcome": "passed", "call": {"longrepr": ""}}]}')
    code = HERE / "sample_code.py"
    readme = HERE / "sample_readme.md"
    try:
        # report_paths/student_files must be tuples — assignment_code is
        # lru_cache'd and needs hashable args (see entrypoint.get_path_tuple).
        n_failed, prompt_str = prompt.engineering((report,), (code,), readme, "English")
    finally:
        report.unlink(missing_ok=True)
    # Rubric against the PROMPT (proxy). Reply-rubric TODO below.
    ok = check_rubric(
        "1. all-passed prompt",
        prompt_str,
        must_contain=["All tests passed", "Do not assign or fabricate scores"],
        must_not_contain=["Error Message Start"],  # no failure block when all pass
    )
    assert n_failed == 0
    # TODO(eval): send prompt_str to provider, then rubric the REPLY:
    #   must praise + suggest 1 improvement; must NOT invent a score.
    return ok


# --- Case 3: ZeroDivisionError (reuse shipped fixture) ------------------------
def case_div_zero():
    report = HERE / "json_dict_div_zero_try_except.json"
    code = HERE / "sample_code.py"
    readme = HERE / "sample_readme.md"
    n_failed, prompt_str = prompt.engineering((report,), (code,), readme, "English")
    ok = check_rubric(
        "3. div-zero prompt",
        prompt_str,
        must_contain=["Error Message Start", "failed"],
        must_not_contain=["All tests passed"],
    )
    assert n_failed >= 1
    # TODO(eval): send prompt_str to provider, then rubric the REPLY:
    #   must identify the unguarded division / missing edge case;
    #   must be in the requested locale; must NOT echo the whole traceback.
    return ok


def main():
    results = [case_all_passed(), case_div_zero()]
    passed = sum(results)
    print(f"\n{passed}/{len(results)} sketch cases passed "
          f"(prompt-level only; reply-scoring is TODO).")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
