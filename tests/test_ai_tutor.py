import json
import pathlib
import sys
import urllib.parse as up

from typing import Callable, Dict, List, Tuple, Union


PYTEST_JSON_REPORT = Dict[str, Union[str, List]]


import pytest


test_folder = pathlib.Path(__file__).parent.resolve()
project_folder = test_folder.parent.resolve()


sys.path.insert(
    0,
    str(project_folder)
)


import ai_tutor



@pytest.fixture
def sample_report_path() -> pathlib.Path:
    return test_folder / 'sample_report.json'


@pytest.fixture
def json_dict(sample_report_path) -> PYTEST_JSON_REPORT:
    with sample_report_path.open('rt') as f:
        result = json.load(f)
    return result


def test_collect_longrepr__returns_non_empty(json_dict:PYTEST_JSON_REPORT):
    result = ai_tutor.collect_longrepr(json_dict)

    assert result


@pytest.fixture
def div_zero_report_path() -> pathlib.Path:
    return test_folder / 'json_dict_div_zero_try_except.json'


@pytest.fixture
def json_dict_div_zero_try_except(div_zero_report_path:pathlib.Path) -> PYTEST_JSON_REPORT:
    with div_zero_report_path.open('rt') as f:
        result = json.load(f)
    return result


def test_collect_longrepr_div_zero_dict__returns_non_empty(json_dict_div_zero_try_except:PYTEST_JSON_REPORT):
    result = ai_tutor.collect_longrepr(json_dict_div_zero_try_except)

    assert result


def test_collect_longrepr_from_multiple_reports__returns_non_empty(
        sample_report_path:pathlib.Path,
        div_zero_report_path:pathlib.Path,
        explanation_in:str
    ):
    multiple_reports = (
        sample_report_path,
        div_zero_report_path
    )
    result = ai_tutor.collect_longrepr_from_multiple_reports(
        multiple_reports,
        explanation_in=explanation_in,
    )

    assert result


@pytest.fixture(params=tuple(path.stem for path in pathlib.Path('locale').glob('*.json')))
def explanation_in(request) -> str:
    return request.param


@pytest.fixture
def homework(explanation_in:str) -> Tuple[str]:
    d = {
        'Korean': ('숙제',),
        'English': ('Homework',),
        'Bahasa Indonesia': ('tugas', 'pekerjaan rumah', 'PR'),
        'Chinese': ('作业',),
        'French': ('Devoir',),
        'German': ('Hausaufgabe',),
        'Italian': ('Compito', 'Compiti'),
        'Japanese': ('宿題',),
        'Nederlands': ('Huiswerk',),
        'Norwegian': ('Hjemmelekse', 'lekser'),
        'Spanish': ('Tarea',),
        'Swedish': ('Läxa',),
        'Thai': ('การบ้าน',),
        'Vietnamese': ('Bài tập',),
    }    
    return tuple(
        map(
            lambda x: x.lower(),
            d[explanation_in]
        )
    )


@pytest.fixture
def msg(explanation_in:str) -> str:
    d = {
        'Korean': '메시지',
        'English': 'Message',
        'Bahasa Indonesia': 'Pesan',
        'Chinese': '消息',
        'French': 'Message',
        'German': 'Fehlermeldung',
        'Italian': 'Messaggio',
        'Japanese': 'メッセ',
        'Nederlands': 'Foutmelding', # error message
        'Norwegian': 'Melding',
        'Spanish': 'Mensaje',
        'Swedish': 'Meddelande',
        'Thai': 'ข้อความ',
        'Vietnamese': 'thông báo', # notification
    }
    return d[explanation_in].lower()


@pytest.fixture
def instruction(explanation_in:str) -> str:
    d = {
        'Korean': ('지침',),
        'English': ('Instruction',),
        'Bahasa Indonesia': ('Petunjuk', 'Instruksi'),
        'Chinese': ('说明',),
        'French': ('instruction',),
        'German': ('Aufgabenanweisung',),
        'Italian': ('istruzione',),
        'Japanese': ('指示',),
        'Nederlands': ('instructie',),
        'Norwegian': ('instruksjon',),
        'Spanish': ('instrucción',),
        'Swedish': ('instruktion',),
        'Thai': ('แนะนำ',),
        'Vietnamese': ('hướng dẫn',),
    }
    return tuple(
        map(
            lambda x: x.lower(),
            d[explanation_in]
        )
    )


def test_get_directive(explanation_in:str, homework:Tuple[str]):
    result = ai_tutor.get_directive(explanation_in=explanation_in)

    assert any(
        map(
            lambda x: x in result.lower(),
            homework
        )
    ), (
        f"Could not find homework: {homework} in result: {result}."
    )


def test_get_instruction(explanation_in:str, homework:Tuple[str],):
    result = ai_tutor.get_directive(explanation_in=explanation_in).lower()

    assert any(
        map(
            lambda x: x in result,
            homework
        )
    ), (
        f"Could not find homework: {homework} in result: {result}."
    )


@pytest.mark.parametrize("func", (ai_tutor.get_report_header, ai_tutor.get_report_footer))
def test_get_report__header__footer(explanation_in:str, msg:str, func:Callable):

    result = func(explanation_in=explanation_in)

    assert msg in result.lower(), f"Could not find msg: {msg} in result: {result}."


@pytest.fixture
def sample_student_code_path() -> pathlib.Path:
    return test_folder / 'sample_code.py'


@pytest.fixture
def sample_readme_path() -> pathlib.Path:
    return test_folder / 'sample_readme.md'


def test_get_instruction_block(
        sample_readme_path:pathlib.Path,
        explanation_in:str,
        instruction:str,
    ):

    result = ai_tutor.get_instruction_block(
        readme_file = sample_readme_path,
        explanation_in=explanation_in
    ).lower()

    assert any(
        map(
            lambda x: x in result,
            instruction
        )
    ), f"Could not find instruction: {instruction} in result: {result}."


def test_get_student_code_block(
        sample_student_code_path:pathlib.Path,
        explanation_in:str,
        homework:Tuple[str],
    ):

    result = ai_tutor.get_student_code_block(
        student_files = (sample_student_code_path,),
        explanation_in=explanation_in
    ).lower()

    assert any(
        map(
            lambda x: x in result,
            homework
        )
    )


def test_get_prompt__has__homework__msg__instruction(
        sample_report_path:pathlib.Path,
        div_zero_report_path:pathlib.Path,
        sample_student_code_path:pathlib.Path,
        sample_readme_path:pathlib.Path,
        explanation_in:str,
        homework:Tuple[str],
        msg:str,
        instruction:str,
    ):
    result = ai_tutor.get_prompt(
        report_paths=(sample_report_path,div_zero_report_path),
        student_files=(sample_student_code_path,),
        readme_file=sample_readme_path,
        explanation_in=explanation_in,
    )

    n_failed = result[0]
    prompe_text = result[1].lower()

    assert any(
        map(
            lambda x: x in prompe_text,
            homework
        )
    )
    assert msg in prompe_text

    assert any(
        map(
            lambda x: x in prompe_text,
            instruction
        )
    ), f"Could not find instruction: {instruction} in result: {prompe_text}."


def test_load_locale(explanation_in:str, homework:Tuple[str]):
    result = ai_tutor.load_locale(explanation_in)

    assert 'directive' in result

    assert any(
        map(
            lambda x: x in result['directive'].lower(),
            homework
        )
    )


@pytest.fixture
def start_marker() -> str:
    return r"``From here is common to all assignments.``"


@pytest.fixture
def end_marker() -> str:
    return r"``Until here is common to all assignments.``"


@pytest.fixture
def common_lines() -> Tuple[str]:
    return (
        "def subtract(a, b):",
        "    return a - b"
    )


@pytest.fixture
def specific_lines() -> Tuple[str]:
    return (
        "Write a function that returns the sum of two numbers.",
        "def add(a, b):",
        "    return a + b"
    )


@pytest.fixture
def common_content_single(
    start_marker:str,
    common_lines:Tuple[str],
    end_marker:str
) -> str:
    return create_common_block(start_marker, common_lines, end_marker)


def create_common_block(
        start_marker:str,
        common_lines:Tuple[str],
        end_marker:str
) -> str:
    return (
        '\n'.join((start_marker,) + common_lines + (end_marker,))
        + '\n'
    )


@pytest.fixture
def readme_content_single(
    specific_lines:Tuple[str],
    common_content_single:str
) -> str:
    return (
        '\n'.join(specific_lines)
        + '\n'
        + common_content_single
    )


def test__exclude_common_contents__single(
    readme_content_single:str,
    start_marker:str,
    end_marker:str,
    specific_lines:Tuple[str],
    common_lines:Tuple[str],
):
    result = ai_tutor.exclude_common_contents(
        readme_content=readme_content_single,
        common_content_start_marker=start_marker,
        common_content_end_marker=end_marker,
    )

    for line in specific_lines:
        assert line.strip() in result, ("\n"
            f"Could not find line: {line}\n"
            f"in result: {result}."
        )

    for line in common_lines:
        assert line.strip() not in result, ("\n"
            f"Found line: {line}\n"
            f"in result: {result}."
        )

    assert start_marker.strip() not in result
    assert end_marker.strip() not in result


def test__exclude_common_contents__single__default_markers(
    readme_content_single:str,
    start_marker:str,
    end_marker:str,
    specific_lines:Tuple[str],
    common_lines:Tuple[str],
):
    result = ai_tutor.exclude_common_contents(
        readme_content=readme_content_single,
    )

    for line in specific_lines:
        assert line.strip() in result, ("\n"
            f"Could not find line: {line}\n"
            f"in result: {result}."
        )

    for line in common_lines:
        assert line.strip() not in result, ("\n"
            f"Found line: {line}\n"
            f"in result: {result}."
        )

    assert start_marker.strip() not in result
    assert end_marker.strip() not in result


@pytest.fixture
def specific_lines_2() -> Tuple[str]:
    """Provides a tuple of specific lines to be inserted between common content blocks."""
    return (
        "// This is specific content between the common blocks.",
        "// It should be preserved in the output."
    )


@pytest.fixture
def readme_content_specific_common_specific(
    readme_content_single:str,
    specific_lines_2:Tuple[str],
) -> str:
    return (
        readme_content_single
        + '\n'.join(specific_lines_2) + '\n'
    )


def test__exclude_common_contents__specific_common_specific(
    readme_content_specific_common_specific:str,
    start_marker:str,
    end_marker:str,
    specific_lines:Tuple[str],
    common_lines:Tuple[str],
    specific_lines_2:Tuple[str],
):
    result = ai_tutor.exclude_common_contents(
        readme_content=readme_content_specific_common_specific,
        common_content_start_marker=start_marker,
        common_content_end_marker=end_marker,
    )

    for line in (specific_lines + specific_lines_2):
        assert line.strip() in result, ("\n"
            f"Could not find line: {line}\n"
            f"in result: {result}."
        )

    for line in common_lines:
        assert line.strip() not in result, ("\n"
            f"Found line: {line}\n"
            f"in result: {result}."
        )

    assert start_marker.strip() not in result
    assert end_marker.strip() not in result


@pytest.fixture
def common_lines_2() -> Tuple[str]:
    return (
        "def div(a, b):",
        "    return a / b"
    )


@pytest.fixture
def readme_content_double(
    readme_content_specific_common_specific:str,
    start_marker:str,
    common_lines_2:Tuple[str],
    end_marker:str
) -> str:
    return (
        readme_content_specific_common_specific
        + create_common_block(start_marker, common_lines_2, end_marker)
    )


def test__exclude_common_contents__double(
    readme_content_double:str,
    start_marker:str,
    end_marker:str,
    specific_lines:Tuple[str],
    specific_lines_2:Tuple[str],
    common_lines:Tuple[str],
    common_lines_2:Tuple[str],
):
    result = ai_tutor.exclude_common_contents(
        readme_content=readme_content_double,
        common_content_start_marker=start_marker,
        common_content_end_marker=end_marker,
    )

    for line in (tuple(specific_lines) + tuple(specific_lines_2)):
        assert line.strip() in result, ("\n"
            f"Could not find line: {line}\n"
            f"in result: {result}."
        )

    for line in (tuple(common_lines) + tuple(common_lines_2)):
        assert line.strip() not in result, ("\n"
            f"Found line: {line}\n"
            f"in result: {result}."
        )

    assert start_marker.strip() not in result
    assert end_marker.strip() not in result


@pytest.fixture
def specific_lines_3() -> Tuple[str]:
    """Provides a tuple of specific lines to be inserted after two common content blocks."""
    return (
        "# This is also specific content, after two common blocks.",
        "# It should be preserved in the output, too."
    )


@pytest.fixture
def readme_content__double_specific(
    readme_content_double:str,
    specific_lines_3:Tuple[str],
) -> str:
    return (
        readme_content_double
        + '\n'.join(specific_lines_3) + '\n'
    )


def test__exclude_common_contents__double_specific(
    readme_content__double_specific:str,
    start_marker:str,
    end_marker:str,
    specific_lines:Tuple[str],
    specific_lines_2:Tuple[str],
    specific_lines_3:Tuple[str],
    common_lines:Tuple[str],
    common_lines_2:Tuple[str],
):
    result = ai_tutor.exclude_common_contents(
        readme_content=readme_content__double_specific,
        common_content_start_marker=start_marker,
        common_content_end_marker=end_marker,
    )

    for line in (specific_lines + specific_lines_2 + specific_lines_3):
        assert line.strip() in result, ("\n"
            f"Could not find line: {line}\n"
            f"in result: {result}."
        )

    for line in (common_lines + common_lines_2):
        assert line.strip() not in result, ("\n"
            f"Found line: {line}\n"
            f"in result: {result}."
        )

    assert start_marker.strip() not in result
    assert end_marker.strip() not in result


@pytest.fixture
def test_api_key() -> str:
    return 'test_api_key'


@pytest.fixture
def expected_default_gemini_model() -> str:
    return 'gemini-2.0-flash'


def test_url__default_model(
        test_api_key:str,
        expected_default_gemini_model:str
    ):
    result = ai_tutor.url(test_api_key)

    result_parsed = up.urlparse(result)

    path_parts = result_parsed.path.split('/')

    b_found = False

    for part in path_parts:
        if expected_default_gemini_model in part.split(':'):
            b_found = True
            break

    assert b_found, f"Could not find {expected_default_gemini_model} in {path_parts}."


def test_url__specific_model(
        test_api_key:str,
    ):
    model = 'gemini-2.0-flash'
    result = ai_tutor.url(test_api_key, model=model)

    result_parsed = up.urlparse(result)

    path_parts = result_parsed.path.split('/')

    b_found = False

    for part in path_parts:
        if model in part.split(':'):
            b_found = True
            break

    assert b_found, f"Could not find {expected_default_gemini_model} in {path_parts}."


@pytest.fixture
def collect_longrepr_result(json_dict:PYTEST_JSON_REPORT) -> List[str]:
    return ai_tutor.collect_longrepr(json_dict)


def test__collect_longrepr__is_list(collect_longrepr_result:List[str]):
    assert isinstance(collect_longrepr_result, list), f"Expected list, got {type(collect_longrepr_result)}."


def test__collect_longrepr__has_list_items(collect_longrepr_result:List[str]):
    assert collect_longrepr_result, "Expected non-empty list, got empty list."


def test__collect_longrepr__has_list_items_len(collect_longrepr_result:List[str]):
    for s in collect_longrepr_result:
        assert isinstance(s, str), f"Expected string, has {s} which is {type(s)}."
        assert s, "Expected non-empty string, got empty string."


def test__collect_longrepr__compare_contents(collect_longrepr_result:List[str]):
    markers = 'longrepr100 longrepr110'.split()
    markers += 'longrepr200 longrepr210'.split()
    markers += 'longrepr300 longrepr310'.split()
    markers += 'longrepr400 longrepr410'.split()
    markers += 'longrepr500 longrepr510 longrepr520'.split()
    markers += 'longrepr600 longrepr610 longrepr620'.split()
    markers += 'longrepr700 longrepr710 longrepr720'.split()
    markers += 'longrepr800 longrepr810 longrepr820'.split()
    markers += 'longrepr900 longrepr910 longrepr920'.split()
    markers += 'longrepr1000 longrepr1010 longrepr1020'.split()
    markers += 'longrepr1100 longrepr1110 longrepr1120'.split()
    markers += 'longrepr1200 longrepr1210 longrepr1220'.split()

    for s in collect_longrepr_result:
        for marker in markers:
            if marker in s:
                markers.remove(marker)

    assert not markers, f"Expected all markers to be found, but missing: {markers}."


if '__main__' == __name__:
    pytest.main([__file__])
