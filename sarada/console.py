"""
Run application from the command line.
"""
from __future__ import annotations

import json
import os
import sys

from pathlib import Path
from typing import Final, Iterable, Iterator

import typer

from keras.engine.training import Model
from loguru import logger

from sarada.logging import setup_logging
from sarada.neuron import Neuron
from sarada.notebook import Notebook, Pitch
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


@app.command()
def prepare(music_dir: Path = arg_music_dir, model_path: Path = arg_model_path) -> None:
    """
    Initialize model directory and prepare data for it.
    """
    setup_logging()

    try:
        notes = read_scores(music_dir)
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


@app.command()
def fit(
    music_dir: Path = arg_music_dir,
    model_path: Path = arg_model_path,
    load_model: bool = arg_load_model,
    epochs: int = arg_epochs,
) -> None:
    """
    Start fitting model with provided source directory.
    """
    setup_logging()

    try:
        notes = read_scores(music_dir)
    except IOError as ex:
        logger.error(str(ex))
        sys.exit(1)

    if not notes:
        logger.error("No data was found")
        raise typer.Exit(1)

    logger.info("Processing datasets")

    numeris = notes.numerize()
    series = numeris.make_series(window_size=window_size)

    model: Model
    if load_model and model_path:
        model = Neuron.load(
            model_path, input_length=window_size, output_length=numeris.distinct_size
        )
    elif load_model:
        logger.error("No path provided to load model")
        raise typer.Exit(1)
    else:
        model = Neuron(input_length=window_size, output_length=numeris.distinct_size)

    model.learn(series, epochs=epochs)

    model.save(model_path)


@app.command()
def generate(
    music_dir: Path = arg_music_dir, model_path: Path = arg_model_path
) -> None:
    """
    Generate sequence from model.
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
        raise typer.Exit(1)

    logger.info("Processing datasets")
    numeris = notes.numerize()

    model = Neuron.load(
        model_path, input_length=window_size, output_length=numeris.distinct_size
    )

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
    logger.info("Storing sequence at {path}", path=path)
    stream = create_stream(pitches)
    logger.debug("Saving file in {path}", path=path)
    stream.write("midi", fp=path)


def read_files(path: Path) -> Iterator[str]:
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
    app()
