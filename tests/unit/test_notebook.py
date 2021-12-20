"""
Tests for categorization tools.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

from hypothesis import given
from hypothesis.strategies import lists

from sarada import music21
from sarada.notebook import Notebook, Score

from .strategies import m21notes


def test_notebook_empty() -> None:
    """Test adding notes to categorizer."""
    notebook = Notebook()
    assert len(notebook) == 0
    assert not notebook


@given(lists(m21notes()))
def test_notebook_add_note(note_list: List[music21.Note]) -> None:
    """Test adding notes to categorizer."""
    notebook = Notebook()
    notebook.add(note_list)

    assert len(notebook) == 1


@given(lists(m21notes()))
def test_notebook_numerizing_denumerizing(note_list: List[music21.Note]) -> None:
    """Test note numerization in notebook."""
    notebook = Notebook()
    notebook.add(note_list)

    numeris = notebook.numerize()

    assert list(numeris.data[0]) == notebook.notes[0]


@given(lists(lists(m21notes()), max_size=5))
def test_notebook_comparison_equals(note_list: List[List[music21.Note]]) -> None:
    """Test comparisin of notebooks."""
    notebook1 = Notebook()
    for notes in note_list:
        notebook1.add(notes)

    notebook2 = Notebook()
    for notes in note_list:
        notebook2.add(notes)

    assert notebook1 == notebook2


@given(lists(lists(m21notes()), min_size=1, max_size=5))
def test_notebook_comparison_not_equals(note_list: List[Score]) -> None:
    """Test comparison of notebooks."""
    notebook1 = Notebook()
    for notes in note_list:
        notebook1.add(notes)

    notebook2 = Notebook()
    for notes in note_list[1:]:
        notebook2.add(notes)

    assert notebook1 != notebook2


@given(lists(lists(m21notes()), min_size=1, max_size=5))
def test_notebook_save_load_works(note_list: List[Score]) -> None:
    """Test loading and saving results in same object."""
    notebook = Notebook()
    for notes in note_list:
        notebook.add(notes)

    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        notebook.store(path)
        loaded = notebook.read(path)

    assert notebook == loaded
