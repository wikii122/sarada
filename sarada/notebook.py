"""
Categorize and normalize notes.
"""
from __future__ import annotations

from typing import Iterable, List, NewType, cast

from loguru import logger
from music21.note import GeneralNote, Note

from sarada.numeris import Numeris

Key = NewType("Key", int)
Pitch = NewType("Pitch", str)
Score = Iterable[GeneralNote]


class Notebook:
    """
    Storage for keeping sets of notes efficiently.

    Allows for storage of notes, pitches to be exact, and perform further operations
    on them, such as for normalization.
    """

    def __init__(self) -> None:
        self.notes: List[List[Pitch]] = []

    def add(self, notes: Score) -> None:
        """
        Add set of notes to processed data.
        """
        noteset: List[Pitch] = []

        for note in notes:
            if isinstance(note, Note):
                pitch: Pitch = cast(Pitch, str(note.pitch))
            else:
                raise NotImplementedError(
                    f"Support for note type { type(note) } not implemented"
                )

            noteset.append(pitch)

        logger.debug("Adding noteset of {} notes", len(noteset))
        self.notes.append(noteset)

    def numerize(self) -> Numeris[Pitch]:
        """
        Create new Numeris from current state of Notebook.
        """
        return Numeris[Pitch](self.notes)

    def __str__(self) -> str:
        return f"<{ self.__class__.__name__ } containing { len(self) } note sets>"

    def __len__(self) -> int:
        return len(self.notes)
