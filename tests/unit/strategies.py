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
        pitch = Pitch(f"{name}{accidental}{octave}")
    else:
        pitch = Pitch(f"{name}{accidental}")

    return pitch


@composite
def pitches(draw) -> music21.Musical:  # type: ignore
    length = draw(integers(min_value=1, max_value=4))
    if length == 1:
        pitch = draw(pitches())
        return Note(pitch)

    pitch = [draw(pitches()) for _ in repeat(None, length)]
    return Chord(pitch)


@composite
def notes(draw) -> music21.Note:  # type: ignore
    length = draw(integers(min_value=1, max_value=4))
    if length == 1:
        pitch = draw(pitches())
        return music21.Note(pitch)

    pitch = [draw(pitches()) for _ in repeat(None, length)]
    return music21.Chord(pitch)
