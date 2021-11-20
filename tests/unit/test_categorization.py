"""
Tests for categorization tools.
"""
from typing import List

from hypothesis import given
from hypothesis.strategies import lists
from music21.note import Note

from sarada.categorization import NoteCategorizer

from .strategies import notes


def test_categorization_empty() -> None:
    """Test adding notes to categorizer"""
    categorizer = NoteCategorizer()
    assert len(categorizer) == 0


@given(lists(notes()))
def test_categorization_add_note(note_list: List[Note]) -> None:
    """Test adding notes to categorizer"""
    categorizer = NoteCategorizer()
    categorizer.add(note_list)

    assert len(categorizer) == 1
