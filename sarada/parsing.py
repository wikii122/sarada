"""
Parse raw file content into workable streams.
"""
from __future__ import annotations

from functools import singledispatch
from pathlib import Path
from typing import Final, Iterable, Iterator, List, Optional

from loguru import logger
from music21 import converter, exceptions21, instrument

from sarada import music21
from sarada.notebook import Chord, Musical, Note, Notebook, Rest

supported_extensions: Final = [
    ".abc",
    ".mxl",
    ".rntxt",
    ".xml",
    ".musicxml",
    ".krn",
    ".midi",
]


def extract_notes(
    scores: Iterable[music21.Stream],
) -> Iterator[Iterator[music21.GeneralNote]]:
    """
    Extract notes from given file contents.
    """
    for score in scores:
        partition = instrument.partitionByInstrument(score)

        notes: Optional[music21.StreamIterator]
        if partition:
            notes = partition.parts[0].recurse()
        else:
            notes = score.flat.notes

        if notes:
            yield (note for note in notes)


def create_stream(pitches: Iterable[Musical]) -> music21.Stream:
    """
    Create stream that may be converted to actual music from pitch list.
    """
    notes: List[music21.GeneralNote] = []
    for idx, pitch in enumerate(pitches):
        note = make_note(pitch)
        note.offset = 0.5 * idx
        note.storedInstrument = instrument.Piano()
        notes.append(note)

    return music21.Stream(notes)


@singledispatch
def make_note(musical: Musical) -> music21.GeneralNote:
    """
    Convert Musical to music21 equivalent.
    """
    raise RuntimeError(f"Dispatch failed for {musical}")


@make_note.register
def make_simple_note(note: Note) -> music21.Note:
    m21note = music21.Note(note.pitch, quarterLength=note.duration)
    return m21note


@make_note.register
def make_chord(chord: Chord) -> music21.Chord:
    m21chord = music21.Chord(chord.pitch, quarterLength=chord.duration)
    return m21chord


@make_note.register
def make_rest(rest: Rest) -> music21.Chord:
    m21rest = music21.Rest(quarterLength=rest.duration)
    return m21rest


def read_scores(path: Path, recursive: bool = False) -> Notebook:
    """
    Open file on given path and aggregate them in Notebook instance.
    """
    logger.info("Processing files in {path}", path=str(path))

    scores = read_files(path, recursive)
    notes_source = extract_notes(scores)

    notes = Notebook()
    for note in notes_source:
        notes.add(note)

    logger.info("Finished loading files")

    return notes


def read_files(path: Path, recursive: bool) -> Iterator[music21.Stream]:
    """
    Iterate over content of musical files in provided directory.
    """
    for filepath in path.iterdir():
        if filepath.is_file() and filepath.suffix in supported_extensions:
            logger.debug("Opening file {path}", path=filepath)
            try:
                score: music21.Stream = converter.parseFile(filepath)
            except IOError as e:
                logger.warning(
                    "Error opening file {path}: {e}", path=str(path), e=str(e)
                )
                continue
            except exceptions21.Music21Exception:
                logger.warning("Could not parse file {path}", path=str(path))
                continue
            yield score
        elif recursive and filepath.is_dir():
            logger.debug("Searching {path}", path=filepath)
            yield from read_files(filepath, recursive=True)
        else:
            logger.debug(
                "File {name} omitted due to unsupported extension", name=filepath
            )


def store_score(pitches: Iterable[Musical], path: Path) -> None:
    """
    Store sequence in midi file.
    """
    logger.info("Storing sequence at {path}", path=path)
    stream = create_stream(pitches)
    logger.debug("Saving file in {path}", path=path)
    stream.write("midi", fp=path)
