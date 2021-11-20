"""
Parse raw file content into workable streams.
"""
from typing import Generator, Iterable, Iterator, Optional

from music21 import converter, instrument
from music21.note import GeneralNote
from music21.stream.base import Stream
from music21.stream.iterator import StreamIterator


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
