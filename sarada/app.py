"""
Run application from the command line.
"""
from pathlib import Path
from typing import Final, Generator

from sarada.categorization import NoteCategorizer
from sarada.parsing import extract_notes

supported_extensions: Final = [".abc"]


def run() -> None:
    """
    Execute code for specified library
    """
    starting_path = (
        "C:\\Users\\wikii\\AppData\\Local\\pypoetry\\Cache\\virtualenvs\\"
        "sarada-h5EBRAqw-py3.10\\Lib\\site-packages\\music21\\corpus\\essenFolksong\\"
    )
    path = Path(starting_path)

    scores = read_files(path)
    notes_source = extract_notes(scores)

    notes = NoteCategorizer()
    for note in notes_source:
        notes.add(note)

    print(notes)


def read_files(path: Path) -> Generator[str, None, None]:
    """
    Iterates over content of musical files in provided directory.
    """
    for filepath in path.iterdir():
        if filepath.is_file() and filepath.suffix in supported_extensions:
            with open(filepath, encoding="utf-8") as audio_file:
                yield audio_file.read()


if __name__ == "__main__":
    run()
