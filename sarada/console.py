"""
Run application from the command line.
"""
from __future__ import annotations

import os
import pickle
import sys

from pathlib import Path
from typing import Final

import typer

from loguru import logger

from sarada.logging import setup_logging
from sarada.neuron import Neuron
from sarada.notebook import Musical
from sarada.numeris import Numeris
from sarada.parsing import read_scores, store_score

app: Final = typer.Typer()

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
    with open(model_path / "data.dat", "wb", encoding="utf-8") as datafile:
        pickle.dump(numeris, datafile)

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

    store_score(pitches)


def load_data(model_path: Path) -> Numeris[Musical]:
    """Parse music files at path given."""
    logger.info("Loading datasets from {path}", path=str(model_path))
    try:
        with open(model_path / "data.dat", "rb", encoding="utf-8") as datafile:
            numeris: Numeris[Musical] = pickle.load(datafile)
    except IOError as ex:
        logger.error(str(ex))
        raise typer.Exit(1)

    return numeris


if __name__ == "__main__":
    app()
