"""
Categorize and normalize notes.
"""
from __future__ import annotations

from typing import Iterable, List, NamedTuple, NewType, Tuple, Union

from loguru import logger

from sarada import music21
from sarada.numeris import Numeris

Key = NewType("Key", int)
Pitch = NewType("Pitch", str)
Score = Iterable[music21.GeneralNote]


class Note(NamedTuple):
    pitch: Pitch


class Chord(NamedTuple):
    pitch: Tuple[Pitch, ...]


Musical = Union[Note, Chord]


class Notebook:
    """
    Storage for keeping sets of notes efficiently.

    Allows for storage of notes, pitch values to be exact, and perform further
    operations on them, such as for normalization.
    """

    def __init__(self) -> None:
        self.notes: List[List[Musical]] = []

    def add(self, notes: Score) -> None:
        """
        Add set of notes to processed data.
        """
        noteset: List[Musical] = []
        musical: Musical
        for note in notes:
            if isinstance(note, music21.Note):
                pitch = Pitch(str(note.pitch))
                musical = Note(pitch)
            elif isinstance(note, music21.Chord):
                pitches = tuple(Pitch(str(n.pitch)) for n in note.notes)
                musical = Chord(pitches)
            elif isinstance(
                note,
                (
                    music21.Instrument,
                    music21.LayoutBase,
                    music21.MiscTandem,
                    music21.SpineComment,
                ),
            ):
                logger.debug("Ignoring note {note}", note=str(note))
                continue
            else:
                logger.warning(
                    "Ignoring score because of unsupported note: {note}", note=str(note)
                )
                return

            noteset.append(musical)

        logger.debug("Adding noteset of {} notes", len(noteset))
        self.notes.append(noteset)

    def numerize(self) -> Numeris[Musical]:
        """
        Create new Numeris from current state of Notebook.
        """
        return Numeris[Musical](self.notes)

    def __str__(self) -> str:
        return f"<{ self.__class__.__name__ } containing { len(self) } note sets>"

    def __len__(self) -> int:
        return len(self.notes)
