"""
Hypothesis strategies definitions.
"""
from __future__ import annotations

from typing import Optional

from hypothesis.strategies import composite, integers, none, sampled_from
from music21.note import Note

from sarada.notebook import Pitch


@composite
def pitches(draw) -> Pitch:  # type: ignore
    name: str = draw(sampled_from("ABCDEFG"))
    accidental: str = draw(sampled_from(["", "#", "-"]))
    octave: Optional[int] = draw(integers(min_value=1, max_value=8) | none())

    if octave:
        pitch = Pitch(f"{name}{accidental}{octave}")
    else:
        pitch = Pitch(f"{name}{accidental}")

    return pitch


@composite
def notes(draw) -> Note:  # type: ignore
    pitch: Pitch = draw(pitches())
    return Note(pitch)
