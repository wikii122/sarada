from __future__ import annotations

from typing import List

from hypothesis import given
from hypothesis.strategies import lists
from music21 import converter

from sarada import music21
from sarada.notebook import Chord, Musical, Note
from sarada.parsing import create_stream, extract_notes
from tests.unit.strategies import chords, notes, rests


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

    musics = converter.parseData(abc)
    notes = next(extract_notes([musics]))
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
    musics = converter.parseData(abc)
    notes = next(extract_notes([musics]))
    next(notes)  # Skip first "A
    next(notes)  # Skip seconda "A

    chord = next(notes)

    assert isinstance(chord, music21.Chord)
    assert len(chord.notes) == 4
    assert chord.figure == "Gm7"  # type: ignore


@given(lists(notes() | chords() | rests()))
def test_create_stream_length(musicals: List[Musical]) -> None:
    stream = create_stream(musicals)
    assert len(stream) == len(musicals)


@given(lists(notes() | chords() | rests()))
def test_create_stream_values(musicals: List[Musical]) -> None:
    stream = create_stream(musicals)
    for note, musical in zip(stream, musicals):
        if isinstance(musical, Note):
            assert str(note.pitch) == musical.pitch
        elif isinstance(musical, Chord):
            assert tuple(str(n.pitch) for n in note.notes) == musical.pitch


@given(lists(notes() | chords() | rests()))
def test_create_stream_durations(musicals: List[Musical]) -> None:
    stream = create_stream(musicals)
    for note, musical in zip(stream, musicals):
        assert note.duration.quarterLength == musical.duration


@given(lists(notes() | chords() | rests()))
def test_create_stream_notes_offsets_notes(pitches: List[Musical]) -> None:
    stream = create_stream(pitches)
    prv: music21.Note
    nxt: music21.Note
    for prv, nxt in zip(stream.notes[:-1], stream.notes[1:]):
        assert nxt.offset - prv.offset > 0
