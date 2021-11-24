"""
Parse raw file content into workable streams.
"""
from __future__ import annotations

from typing import Generator, Iterable, Iterator, List, Optional

from music21 import converter, instrument
from music21.note import GeneralNote, Note
from music21.stream import Stream
from music21.stream.iterator import StreamIterator

from sarada.notebook import Pitch


def extract_notes(
    scores: Iterable[str],
) -> Generator[Iterator[GeneralNote], None, None]:
    """
    Extract notes from given file contents.
    """
    for raw in scores:
        stream: Stream = converter.parseData(raw)
        score = instrument.partitionByInstrument(stream)

        notes: Optional[StreamIterator]
        if score:
            notes = score.parts[0].recurse()
        else:
            notes = stream.flat.notes

        if notes:
            yield (note for note in notes)


def create_stream(pitches: Iterable[Pitch]) -> Stream:
    """
    Create stream that may be converted to actual music from pitch list.
    """
    notes: List[Note] = []
    for idx, pitch in enumerate(pitches):
        note = Note(pitch)
        note.offset = 0.5 * idx
        note.storedInstrument = instrument.Piano()
        notes.append(note)

    return Stream(notes)
