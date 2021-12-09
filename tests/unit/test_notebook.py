"""
Tests for categorization tools.
"""
from __future__ import annotations

from typing import List

from hypothesis import HealthCheck, given, settings
from hypothesis.strategies import lists

from sarada import music21
from sarada.notebook import Notebook

from .strategies import notes


def test_notebook_empty() -> None:
    """Test adding notes to categorizer."""
    notebook = Notebook()
    assert len(notebook) == 0
    assert not notebook


# Supressing health check because drawing multiple values for each list item triggers it
@given(lists(notes()))
@settings(suppress_health_check=(HealthCheck.too_slow, HealthCheck.filter_too_much))
def test_notebook_add_note(note_list: List[music21.Note]) -> None:
    """Test adding notes to categorizer."""
    notebook = Notebook()
    notebook.add(note_list)

    assert len(notebook) == 1


@given(lists(notes()))
@settings(suppress_health_check=(HealthCheck.too_slow, HealthCheck.filter_too_much))
def test_notebook_numerizing_denumerizing(note_list: List[music21.Note]) -> None:
    """Test note numerization in notebook."""
    notebook = Notebook()
    notebook.add(note_list)

    numeris = notebook.numerize()

    assert list(numeris.data[0]) == notebook.notes[0]
