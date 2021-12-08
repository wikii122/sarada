"""
Parse raw file content into workable streams.
"""
from __future__ import annotations

from typing import Iterable, Iterator, List, Optional

from music21 import converter, instrument

from sarada import music21
from sarada.notebook import Pitch


def extract_notes(
    scores: Iterable[str],
) -> Iterator[Iterator[music21.GeneralNote]]:
    """
    Extract notes from given file contents.
    """
    for raw in scores:
        stream: music21.Stream = converter.parseData(raw)
        score = instrument.partitionByInstrument(stream)

        notes: Optional[music21.StreamIterator]
        if score:
            notes = score.parts[0].recurse()
        else:
            notes = stream.flat.notes

        if notes:
            yield (note for note in notes)


def create_stream(pitches: Iterable[Pitch]) -> music21.Stream:
    """
    Create stream that may be converted to actual music from pitch list.
    """
    notes: List[music21.Note] = []
    for idx, pitch in enumerate(pitches):
        note = music21.Note(pitch)
        note.offset = 0.5 * idx
        note.storedInstrument = instrument.Piano()
        notes.append(note)

    return music21.Stream(notes)
