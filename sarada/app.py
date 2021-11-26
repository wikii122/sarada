"""
Run application from the command line.
"""
from __future__ import annotations

import sys

from pathlib import Path
from typing import Final, Generator, Iterable

import typer

from loguru import logger

from sarada.logging import setup_logging
from sarada.neuron import Neuron
from sarada.notebook import Notebook, Pitch
from sarada.parsing import create_stream, extract_notes

supported_extensions: Final = [".abc"]
window_size: Final = 100

arg_music_dir = typer.Argument(..., help="Path to directory containing learnign data")


def main(music_dir: str = arg_music_dir) -> None:
    """
    Execute code for specified library.
    """
    setup_logging()

    path = Path(music_dir)

    try:
        notes = read_scores(path)
    except IOError as ex:
        logger.error(str(ex))
        sys.exit(1)

    if not notes:
        logger.error("No data was found")
        sys.exit(1)

    logger.info("Processing datasets")

    numeris = notes.numerize()
    series = numeris.make_series(window_size=window_size)

    model = Neuron(input_length=window_size, output_length=numeris.distinct_size)
    model.learn(series)

    sequence = model.generate(100)
    pitches = numeris.denumerize(sequence)

    store_sequence(pitches)


def read_scores(path: Path) -> Notebook:
    """
    Open file on given path and aggregate them in Notebook instance.
    """
    logger.info("Processing files in {path}", path=str(path))

    scores = read_files(path)
    notes_source = extract_notes(scores)

    notes = Notebook()
    for note in notes_source:
        notes.add(note)

    logger.info("Finished loading files")

    return notes


def store_sequence(pitches: Iterable[Pitch]) -> None:
    """
    Store sequence in midi file.
    """
    path = "test_output.mid"
    logger.info("storing sequence at {path}", path=path)
    stream = create_stream(pitches)
    logger.debug("Saving file in {path}", path=path)
    stream.write("midi", fp=path)


def read_files(path: Path) -> Generator[str, None, None]:
    """
    Iterate over content of musical files in provided directory.
    """
    for filepath in path.iterdir():
        logger.debug("Opening file {path}", path=filepath)
        if filepath.is_file() and filepath.suffix in supported_extensions:
            with open(filepath, encoding="utf-8") as audio_file:
                yield audio_file.read()
        else:
            logger.debug(
                "File {name} omitted due to unsupported extension", name=filepath
            )


if __name__ == "__main__":
    typer.run(main)
