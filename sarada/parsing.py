"""
Parse raw file content into workable streams.
"""
from __future__ import annotations

from functools import singledispatch
from pathlib import Path
from typing import Final, Iterable, Iterator, List, Optional

from loguru import logger
from music21 import converter, instrument

from sarada import music21
from sarada.notebook import Chord, Musical, Note, Notebook

supported_extensions: Final = [".abc"]


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
    raise RuntimeError(f"Dispatch failed for {musical}")


@make_note.register
def make_simple_note(note: Note) -> music21.Note:
    return Note(note.pitch)


@make_note.register
def make_chord(chord: Chord) -> music21.Chord:
    return Chord(chord.pitch)


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


def read_files(path: Path, recursive: bool) -> Iterator[str]:
    """
    Iterate over content of musical files in provided directory.
    """
    for filepath in path.iterdir():
        if filepath.is_file() and filepath.suffix in supported_extensions:
            logger.debug("Opening file {path}", path=filepath)
            with open(filepath, encoding="utf-8") as audio_file:
                yield audio_file.read()
        elif recursive and filepath.is_dir():
            logger.debug("Searching {path}", path=filepath)
            yield from read_files(filepath, recursive=True)
        else:
            logger.debug(
                "File {name} omitted due to unsupported extension", name=filepath
            )


def store_score(pitches: Iterable[Musical]) -> None:
    """
    Store sequence in midi file.
    """
    path = "test_output.mid"
    logger.info("Storing sequence at {path}", path=path)
    stream = create_stream(pitches)
    logger.debug("Saving file in {path}", path=path)
    stream.write("midi", fp=path)
