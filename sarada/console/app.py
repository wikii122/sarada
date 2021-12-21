"""
Run application from the command line.
"""
from __future__ import annotations

import os
import sys

from pathlib import Path
from typing import Final, Iterable

import typer

from loguru import logger

from sarada.console import config as conf
from sarada.logging import setup_logging
from sarada.neuron import Neuron
from sarada.notebook import Notebook
from sarada.parsing import read_scores, store_score

app: Final = typer.Typer()

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
arg_windows_size = typer.Option(40, help="Size fo window iterating over datasets")
arg_generate_name = typer.Option(
    Path("out.midi"), "-o", "--output", help="Name of generated file"
)
arg_generate_length = typer.Option(120, help="Length of generated sequence in notes")
arc_generate_number = typer.Option(1, help="Number of files to generate")


@app.command()
def prepare(
    music_dir: Path = arg_music_dir,
    model_path: Path = arg_model_path,
    recursive: bool = arg_recursive,
    window_size: int = arg_windows_size,
) -> None:
    """
    Initialize model directory and prepare data for it.
    """
    setup_logging()

    if window_size <= 0:
        logger.error("Window size must be positive")
        raise typer.Exit(1)

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

    os.mkdir(model_path)
    notes.store(model_path)
    numeris = notes.numerize()

    model = Neuron(input_length=window_size, output_length=numeris.distinct_size)
    model.save(model_path / "model")

    config: conf.ConfigData = {"iterations": 0, "window_size": window_size}
    conf.store(config, model_path)

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
    config: Final = conf.read(model_path)
    window_size: Final[int] = config["window_size"]

    notebook = Notebook.read(model_path)
    numeris = notebook.numerize()
    model = Neuron.load(
        model_path / "model",
        input_length=window_size,
        output_length=numeris.distinct_size,
    )

    series = numeris.make_series(window_size=window_size)
    model.learn(series, epochs=epochs)
    model.save(model_path / "model")

    config["iterations"] += epochs
    conf.store(config, model_path)


@app.command()
def generate(
    model_path: Path = arg_model_path,
    output: Path = arg_generate_name,
    length: int = arg_generate_length,
    count: int = arc_generate_number,
) -> None:
    """
    Generate sequence from model.
    """
    setup_logging()
    config: Final = conf.read(model_path)
    window_size: Final[int] = config["window_size"]

    notebook = Notebook.read(model_path)
    numeris = notebook.numerize()
    model = Neuron.load(
        model_path / "model",
        input_length=window_size,
        output_length=numeris.distinct_size,
    )

    for path in filenames(output, count):
        sequence = model.generate(length)
        pitches = numeris.denumerize(sequence)

        store_score(pitches, path)


def filenames(path: Path, count: int) -> Iterable[Path]:
    """
    Generate given number of filename.

    >>> [str(p) for p in filenames(Path("a.mid"), 1)]
    ['a.mid']

    >>> [str(p) for p in filenames(Path("a.mid"), 2)]
    ['a-1.mid', 'a-2.mid']
    """
    if count > 1:
        for i in range(1, count + 1):
            yield Path(f"{path.stem}-{i}{path.suffix}")
    else:
        yield path


if __name__ == "__main__":
    app()
