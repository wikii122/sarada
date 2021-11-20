"""
Hypothesis strategies definitions
"""
from typing import Optional

from hypothesis.strategies import composite, integers, none, sampled_from
from music21.note import Note


@composite
def notes(draw) -> Note:  # type: ignore
    name: str = draw(sampled_from("ABCDEFG"))
    accidental: str = draw(sampled_from(["", "#", "-"]))
    octave: Optional[int] = draw(integers(min_value=1, max_value=8) | none())

    if octave:
        pitch = f"{name}{accidental}{octave}"
    else:
        pitch = f"{name}{accidental}"

    return Note(pitchName=pitch)
