from typing import Generic, List, Tuple, TypeVar

T = TypeVar("T")


class Numeris(Generic[T]):
    """
    Keep order of numeric data and allows to perform operation on those.

    Most notably allows to change values back and forth into ordered numerics.
    """

    def __init__(self, data: List[List[T]]):
        self._data: Tuple[Tuple[T]] = tuple(tuple(d) for d in data)

    @property
    def data(self) -> Tuple[Tuple[T]]:
        return self._data
