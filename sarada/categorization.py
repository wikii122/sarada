"""
Categorize and normalize notes.
"""

from typing import Dict, Iterable, List, NewType, cast

from music21.note import GeneralNote, Note

Key = NewType("Key", int)
Pitch = NewType("Pitch", str)
Score = Iterable[GeneralNote]


class NoteCategorizer:
    """
    Storage for keeping sets of notes efficiently and allowing
    for normalization of them.
    """

    def __init__(self) -> None:
        self.note_key: Dict[Pitch, Key] = {}
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

        self.notes.append(noteset)

    def __str__(self) -> str:
        return f"<{ self.__class__ } containing { len(self) } note sets>"

    def __len__(self) -> int:
        return len(self.notes)
