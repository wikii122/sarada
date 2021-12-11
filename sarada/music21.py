"""
Combined imports from music21.
"""
from __future__ import annotations

# pylint: disable=useless-suppression,import-error
from music21.chord import Chord
from music21.humdrum.spineParser import MiscTandem, SpineComment
from music21.instrument import Instrument
from music21.layout import LayoutBase
from music21.note import GeneralNote, Note
from music21.stream import Stream
from music21.stream.iterator import StreamIterator

__all__ = [
    "Chord",
    "GeneralNote",
    "Instrument",
    "LayoutBase",
    "MiscTandem",
    "Note",
    "SpineComment",
    "Stream",
    "StreamIterator",
]
