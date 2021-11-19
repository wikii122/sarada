"""
Parse raw file content into workable streams.
"""
from typing import Generator, Iterable, Optional

from music21 import converter, instrument
from music21.stream import Stream


def extract_notes(scores: Iterable[str]) -> Generator[Stream, None, None]:
    """
    Extract notes from given file contents.
    """
    for raw in scores:
        stream = converter.parseData(raw)
        score = instrument.partitionByInstrument(stream)

        notes: Optional[Stream]
        if score:
            notes = score.parts[0].recurse()
        else:
            notes = stream.flat.notes

        if notes:
            yield notes
