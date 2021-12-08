from __future__ import annotations

from typing import List

from hypothesis import given
from hypothesis.strategies import lists

from sarada import music21
from sarada.notebook import Pitch
from sarada.parsing import create_stream, extract_notes
from tests.unit.strategies import pitches


def test_extract_note_pitch() -> None:
    """Check if note pitch is extracted."""
    abc = """
    X:1
    T:Notes / pitches
    M:C
    L:1/4
    K:C treble
    C, D, E, F, | G, A, B, C
    """

    notes = next(extract_notes([abc]))
    note = next(notes)

    assert isinstance(note, music21.Note)
    assert note.pitch.step == "C"
    assert note.pitch.octave == 3


def test_extract_note_chords() -> None:
    """Check if note chords are extracted."""
    abc = """
    X:1
    T:Chord symbols
    M:C
    K:C
    "A"A "Gm7"D "Bb"F "F#"A |]
    """

    notes = next(extract_notes([abc]))
    next(notes)  # Skip first "A
    next(notes)  # Skip seconda "A

    chord = next(notes)

    assert isinstance(chord, music21.Chord)
    assert len(chord.notes) == 4
    assert chord.figure == "Gm7"  # type: ignore


@given(lists(pitches()))
def test_create_stream_length_and_values(pitches: List[Pitch]) -> None:
    stream = create_stream(pitches)
    assert len(stream.notes) == len(pitches)
    for note, pitch in zip(stream.notes, pitches):
        assert str(note.pitch) == pitch


@given(lists(pitches()))
def test_create_stream_notes_offsets(pitches: List[Pitch]) -> None:
    stream = create_stream(pitches)
    prv: music21.Note
    nxt: music21.Note
    for prv, nxt in zip(stream.notes[:-1], stream.notes[1:]):
        assert nxt.offset - prv.offset == 0.5
