"""
Run application from the command line.
"""
from __future__ import annotations

import json
import os
import sys

from pathlib import Path
from typing import Final, Iterable, Iterator, List

import typer

from loguru import logger

from sarada.logging import setup_logging
from sarada.neuron import Neuron
from sarada.notebook import Notebook, Pitch
from sarada.numeris import Numeris
from sarada.parsing import create_stream, extract_notes

app = typer.Typer()

supported_extensions: Final = [".abc"]
window_size: Final = 100

arg_music_dir = typer.Argument(..., help="Path to directory containing learnign data")
arg_model_path = typer.Argument(Path("model/"), help="Path to store model")
arg_load_model = typer.Option(
    False,
    help="If true model will be loaded from model_path",
)
arg_epochs = typer.Option(100, help="Number of epochs to run")
arg_recursive = typer.Option(
    False, "--recursive", "-r", help="Search directories recursively"
)


@app.command()
def prepare(
    music_dir: Path = arg_music_dir,
    model_path: Path = arg_model_path,
    recursive: bool = arg_recursive,
) -> None:
    """
    Initialize model directory and prepare data for it.
    """
    setup_logging()

    if model_path.exists():
        logger.error("Provided path already exists, aborting preparing model")
        raise typer.Exit(1)

    try:
        notes = read_scores(music_dir, recursive)
    except IOError as ex:
        logger.error(str(ex))
        sys.exit(1)

    if not notes:
        logger.error("No data was found")
        raise typer.Exit(1)

    logger.info("Processing datasets")

    numeris = notes.numerize()

    os.mkdir(model_path)
    with open(model_path / "data.json", "x", encoding="utf-8") as datafile:
        json.dump(numeris.data, datafile)

    model = Neuron(input_length=window_size, output_length=numeris.distinct_size)
    model.save(model_path / "model")

    logger.info("Initialized model at path {path}", path=str(model_path))


@app.command()
def fit(
    model_path: Path = arg_model_path,
    epochs: int = arg_epochs,
) -> None:
    """
    Start fitting model with provided source directory.
    """
    setup_logging()

    numeris = load_data(model_path)
    model = Neuron.load(
        model_path / "model",
        input_length=window_size,
        output_length=numeris.distinct_size,
    )

    series = numeris.make_series(window_size=window_size)
    model.learn(series, epochs=epochs)
    model.save(model_path / "model")


@app.command()
def generate(model_path: Path = arg_model_path) -> None:
    """
    Generate sequence from model.
    """
    setup_logging()

    numeris = load_data(model_path)
    model = Neuron.load(
        model_path, input_length=window_size, output_length=numeris.distinct_size
    )

    sequence = model.generate(100)
    pitches = numeris.denumerize(sequence)

    store_sequence(pitches)


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


def store_sequence(pitches: Iterable[Pitch]) -> None:
    """
    Store sequence in midi file.
    """
    path = "test_output.mid"
    logger.info("Storing sequence at {path}", path=path)
    stream = create_stream(pitches)
    logger.debug("Saving file in {path}", path=path)
    stream.write("midi", fp=path)


def load_data(model_path: Path) -> Numeris[Pitch]:
    """Parse music files at path given."""
    logger.info("Loading datasets from {path}", path=str(model_path))
    try:
        with open(model_path / "data.json", "r", encoding="utf-8") as datafile:
            data: List[List[Pitch]] = json.load(datafile)
    except IOError as ex:
        logger.error(str(ex))
        raise typer.Exit(1)

    numeris = Numeris(data)

    return numeris


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


if __name__ == "__main__":
    app()
