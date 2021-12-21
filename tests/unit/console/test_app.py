from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import Union

from hypothesis import given
from hypothesis.strategies._internal.numbers import integers
from hypothesis_fspaths import fspaths

from sarada.console.app import filenames

max_value = 10000


@given(fspaths())
def test_filenames_single_file(pathstr: Union[str, bytes, PathLike]) -> None:
    """Single file output should return same path."""
    path = Path(str(pathstr))
    paths = list(filenames(path, 1))
    assert paths[0] == path


@given(fspaths(), integers(min_value=2, max_value=max_value))
def test_filenames_multiple_files_names(
    pathstr: Union[str, bytes, PathLike], count: int
) -> None:
    """Multiple files output should preserve filenames."""
    path = Path(str(pathstr))
    paths = list(filenames(path, count))
    assert all(p.stem.startswith(path.stem) for p in paths)


@given(fspaths(), integers(min_value=2, max_value=max_value))
def test_filenames_multiple_files_extensions(
    pathstr: Union[str, bytes, PathLike], count: int
) -> None:
    """Multiple file output should preserve extension."""
    path = Path(str(pathstr))
    paths = list(filenames(path, count))
    assert all(p.suffix == path.suffix for p in paths)


@given(fspaths(), integers(min_value=1, max_value=max_value))
def test_filenames_length(pathstr: Union[str, bytes, PathLike], count: int) -> None:
    """Number of paths generated should be equal to desired."""
    path = Path(str(pathstr))
    paths = list(filenames(path, count))
    assert len(paths) == count


@given(fspaths(), integers(min_value=2, max_value=max_value))
def test_filenames_single_multiple_files_unique_names(
    pathstr: Union[str, bytes, PathLike], count: int
) -> None:
    """Each path should be unique."""
    path = Path(str(pathstr))
    paths = list(filenames(path, count))
    assert len(set(paths)) == count
