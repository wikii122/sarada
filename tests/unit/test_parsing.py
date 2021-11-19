from music21.chord import Chord
from music21.note import Note

from sarada.parsing import extract_notes


def test_extract_note_pitch():
    """Check if note pitch is extracted"""
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

    assert isinstance(note, Note)
    assert note.pitch.step == "D"
    assert note.pitch.octave == 3


def test_extract_note_chords():
    """Check if note chords are extracted"""
    abc = """
    X:1
    T:Chord symbols
    M:C
    K:C
    "A"A "Gm7"D "Bb"F "F#"A |]
    """

    notes = next(extract_notes([abc]))
    next(notes)  # Skip first "A

    chord = next(notes)

    print(chord.__dict__)
    assert isinstance(chord, Chord)
    assert len(chord.notes) == 4
    assert chord.figure == "Gm7"
