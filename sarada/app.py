"""
Run application from the command line.
"""
import sys
from pathlib import Path
from typing import Final, Generator, Iterable

from loguru import logger

from sarada.neuron import Neuron
from sarada.notebook import Notebook, Pitch
from sarada.parsing import create_stream, extract_notes

supported_extensions: Final = [".abc"]
window_size: Final = 100


def run() -> None:
    """
    Execute code for specified library.
    """
    starting_path = (
        "C:\\Users\\wikii\\AppData\\Local\\pypoetry\\Cache\\virtualenvs\\"
        "sarada-h5EBRAqw-py3.9\\Lib\\site-packages\\music21\\corpus\\essenFolksong\\"
    )
    path = Path(starting_path)

    logger.info("Processing files in {path}", path=str(path))
    notes = read_scores(path)
    logger.info("Finished loading files")

    if not notes:
        logger.error("No data was found")
        sys.exit(1)

    logger.info("Starting processing data")

    numeris = notes.numerize()
    series = numeris.make_series(window_size=window_size)

    logger.info("Starting teaching model")

    model = Neuron(input_length=window_size, output_length=numeris.distinct_size)
    model.learn(series)

    logger.info("Learning finished")

    logger.info("Starting generating data")
    sequence = model.generate(100)

    logger.info("Storing generated data")
    pitches = numeris.denumerize(sequence)
    store_sequence(pitches)


def read_scores(path: Path) -> Notebook:
    """
    Open file on given path and aggregate them in Notebook instance.
    """
    scores = read_files(path)
    notes_source = extract_notes(scores)

    notes = Notebook()
    for note in notes_source:
        notes.add(note)

    return notes


def store_sequence(pitches: Iterable[Pitch]) -> None:
    """
    Store sequence in midi file.
    """
    stream = create_stream(pitches)
    path = "test_output.mid"
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


if __name__ == "__main__":
    run()
