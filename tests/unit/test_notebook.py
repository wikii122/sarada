"""
Tests for categorization tools.
"""
from __future__ import annotations

from typing import List

from hypothesis import given
from hypothesis.strategies import lists

from sarada import music21
from sarada.notebook import Notebook

from .strategies import notes


def test_notebook_empty() -> None:
    """Test adding notes to categorizer."""
    notebook = Notebook()
    assert len(notebook) == 0
    assert not notebook


@given(lists(notes()))
def test_notebook_add_note(note_list: List[music21.Note]) -> None:
    """Test adding notes to categorizer."""
    notebook = Notebook()
    notebook.add(note_list)

    assert len(notebook) == 1


@given(lists(notes()))
def test_notebook_numerizing_denumerizing(note_list: List[music21.Note]) -> None:
    """Test note numerization in notebook."""
    notebook = Notebook()
    notebook.add(note_list)

    numeris = notebook.numerize()

    assert list(numeris.data[0]) == notebook.notes[0]
