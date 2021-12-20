"""
Categorize and normalize notes.
"""
from __future__ import annotations

import pickle

from pathlib import Path
from typing import Final, Iterable, List, NamedTuple, NewType, Optional, Tuple, Union

from loguru import logger

from sarada import music21
from sarada.numeris import Numeris

Key = NewType("Key", int)
Pitch = NewType("Pitch", str)
Score = Iterable[music21.GeneralNote]

filename: Final = "notebook.dat"


class Note(NamedTuple):
    pitch: Pitch


class Chord(NamedTuple):
    pitch: Tuple[Pitch, ...]


Musical = Union[Note, Chord]
Musicals = List[Musical]


class Notebook:
    """
    Storage for keeping sets of notes efficiently.

    Allows for storage of notes, pitch values to be exact, and perform further
    operations on them, such as for normalization.
    """

    def __init__(self, *, notes: Optional[List[Musicals]] = None) -> None:
        if notes is None:
            notes = []

        self.notes: List[Musicals] = notes

    def add(self, notes: Score) -> None:
        """
        Add set of notes to processed data.
        """
        noteset: Musicals = []
        musical: Musical
        for note in notes:
            if isinstance(note, music21.Note):
                pitch = Pitch(str(note.pitch))
                musical = Note(pitch)
            elif isinstance(note, music21.Chord):
                pitches = tuple(Pitch(str(n.pitch)) for n in note.notes)
                musical = Chord(pitches)
            else:
                logger.debug("Ignoring note {note}", note=str(note))
                continue

            noteset.append(musical)

        logger.debug("Adding noteset of {} notes", len(noteset))
        self.notes.append(noteset)

    def numerize(self) -> Numeris[Musical]:
        """
        Create new Numeris from current state of Notebook.
        """
        return Numeris[Musical](self.notes)

    @classmethod
    def read(cls, path: Path) -> Notebook:
        """
        Read notebook data from model folder.
        """
        with open(path / filename, "rb") as datafile:
            notes: List[Musicals] = pickle.load(datafile)

        return cls(notes=notes)

    def store(self, path: Path) -> None:
        """
        Save notebook content in model folder.
        """
        with open(path / filename, "wb") as datafile:
            pickle.dump(self.notes, datafile)

    def __str__(self) -> str:
        return f"<{ self.__class__.__name__ } containing { len(self) } note sets>"

    def __len__(self) -> int:
        return len(self.notes)

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, Notebook):
            return False

        return self.notes == obj.notes
