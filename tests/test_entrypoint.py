import logging
import os
import pathlib
import sys

from typing import Tuple


import pytest


sys.path.insert(
    0,
    str(pathlib.Path(__file__).parent.parent.resolve())
)


import entrypoint


PATH_TUPLE = Tuple[pathlib.Path]
PATH_TUPLE_STR = Tuple[PATH_TUPLE, str]


@pytest.fixture
def path_tuple(tmp_path) -> PATH_TUPLE_STR:
    s = [
        tmp_path / 'file1.txt',
        tmp_path / 'file2.txt',
        tmp_path / 'file3.txt',
    ]

    t = f'{s[0]},{s[1]},{s[2]}'

    return s, t


def test_get_path_tuple__normal(path_tuple:PATH_TUPLE_STR) -> None:
    # Setup
    s, t = path_tuple
    s[0].write_text('file1')
    s[1].write_text('file2')
    s[2].write_text('file3')

    # When
    result = entrypoint.get_path_tuple(t)

    # Then
    assert len(result) == len(s)
    assert all(map(lambda x_y: x_y[0] == x_y[1], zip(result, s)))


def test_get_path_tuple__one_missing(path_tuple:PATH_TUPLE_STR, caplog) -> None:
    # Setup
    caplog.set_level(logging.WARNING)
    s, t = path_tuple
    s[0].write_text('file1')
    s[1].write_text('file2')

    if s[2].exists():
        s[2].unlink()

    # function under test
    result = entrypoint.get_path_tuple(t)

    # Then
    assert result == (s[0], s[1])
    assert 'file3.txt does not exist' in caplog.text


def test_get_path_tuple__all_missing(path_tuple:PATH_TUPLE_STR, caplog) -> None:
    # Setup
    s, t = path_tuple
    for path in s:
        if path.exists():
            path.unlink()

    # Then
    with pytest.raises(ValueError) as e:
        _ = entrypoint.get_path_tuple(t)

    assert 'No valid paths provided' in str(e.value)


if __name__ == '__main__':
    pytest.main([__file__])
