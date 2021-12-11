"""
Hypothesis strategies definitions.
"""
from __future__ import annotations

from itertools import repeat
from typing import Optional

from hypothesis.strategies import composite, integers, none, sampled_from

from sarada import music21
from sarada.notebook import Chord, Note, Pitch


@composite
def raw_pitches(draw) -> Pitch:  # type: ignore
    name: str = draw(sampled_from("ABCDEFG"))
    accidental: str = draw(sampled_from(["", "#", "-"]))
    octave: Optional[int] = draw(integers(min_value=1, max_value=8) | none())

    if octave:
        pitch = f"{name}{accidental}{octave}"
    else:
        pitch = f"{name}{accidental}"

    return Pitch(pitch)


@composite
def notes(draw) -> music21.Note:  # type: ignore
    pitch = draw(raw_pitches())

    return Note(pitch)


@composite
def chords(draw) -> music21.Chord:  # type: ignore
    length = draw(integers(min_value=2, max_value=4))
    pitch = tuple(draw(raw_pitches()) for _ in repeat(None, length))

    return Chord(pitch)


@composite
def m21notes(draw) -> music21.Note:  # type: ignore
    length = draw(integers(min_value=1, max_value=4))
    if length == 1:
        pitch = draw(raw_pitches())
        return music21.Note(pitch)

    pitch = [draw(raw_pitches()) for _ in repeat(None, length)]
    return music21.Chord(pitch)
