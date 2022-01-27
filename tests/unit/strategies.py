"""
Hypothesis strategies definitions.
"""
from __future__ import annotations

from itertools import repeat
from typing import Optional

from hypothesis.strategies import composite, integers, none, sampled_from

from sarada import music21
from sarada.notebook import Chord, Note, Pitch, Rest


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
def notes(draw) -> Note:  # type: ignore
    pitch = draw(raw_pitches())
    duration = draw(sampled_from([0.25, 0.5, 0.75, 1.0]))

    return Note(duration, pitch)


@composite
def chords(draw) -> Chord:  # type: ignore
    length = draw(integers(min_value=2, max_value=4))
    pitch = tuple(draw(raw_pitches()) for _ in repeat(None, length))
    duration = draw(sampled_from([0.25, 0.5, 0.75, 1.0]))

    return Chord(duration, pitch)


@composite
def rests(draw) -> Rest:  # type: ignore
    duration = draw(sampled_from([0.25, 0.5, 0.75, 1.0]))

    return Rest(duration)


@composite
def m21notes(draw) -> music21.Note:  # type: ignore
    length = draw(integers(min_value=0, max_value=4))
    if length == 0:
        return music21.Rest()
    if length == 1:
        pitch = draw(raw_pitches())
        return music21.Note(pitch)

    pitch = [draw(raw_pitches()) for _ in repeat(None, length)]
    return music21.Chord(pitch)
