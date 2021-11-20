"""
Run application from the command line.
"""
import sys
from pathlib import Path
from typing import Final, Generator

from loguru import logger

from sarada.notebook import Notebook
from sarada.parsing import extract_notes

supported_extensions: Final = [".abc"]
window_size: Final = 100


def run() -> None:
    """
    Execute code for specified library.
    """
    starting_path = (
        "C:\\Users\\wikii\\AppData\\Local\\pypoetry\\Cache\\virtualenvs\\"
        "sarada-h5EBRAqw-py3.10\\Lib\\site-packages\\music21\\corpus\\essenFolksong\\"
    )
    path = Path(starting_path)
    logger.info("Processing files in {path}", path=str(path))

    scores = read_files(path)
    notes_source = extract_notes(scores)

    notes = Notebook()
    for note in notes_source:
        notes.add(note)

    logger.info("Finish loading files")

    if not notes:
        logger.error("No data was found")
        sys.exit(1)

    logger.info("Starting processing data")

    numeris = notes.numerize()
    series = numeris.make_series(window_size=window_size)

    print(series)


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
