"""
Simple utility for dataset manipulations and storage.
"""
from __future__ import annotations

from typing import (
    Dict,
    Final,
    Generator,
    Generic,
    Iterable,
    List,
    NamedTuple,
    Tuple,
    TypeVar,
)

T = TypeVar("T")

Dataset = Tuple[Tuple[T, ...], ...]


class Numeris(Generic[T]):
    """
    Keep order of numeric data and allows to perform operation on those.

    Most notably allows to change values back and forth into ordered numerics.
    """

    def __init__(self, data: List[List[T]]):
        self.data: Final[Dataset] = tuple(tuple(d) for d in data)

    def make_series(self, window_size: int = 100) -> Generator[Series, None, None]:
        """
        Generate series of overlapping datasets from data using crawling windows.

        Resulting data will contain input and output where output will be input shifted
        by one. For instance "abcdefg" with window size 5 will generate 2 datasets, one
        with input 'abcde' and output 'bcdef' and second with input 'bcdef' and output
        'cdefg'. Then it replaces these values with ordered numeric values using
        numerization functions.

        >>> numeris = Numeris(["abcdefg"])
        >>> series = numeris.make_series(window_size=5)

        >>> next(series)
        Series(input=[0, 1, 2, 3, 4], output=[1, 2, 3, 4, 5])

        >>> next(series)
        Series(input=[1, 2, 3, 4, 5], output=[2, 3, 4, 5, 6])

        >>> next(series)
        Traceback (most recent call last):
            ...
        StopIteration
        """

        for dataset in self.data:
            numerized = self.numerize(dataset)
            inps = numerized[:window_size]
            for idx in range(1, len(numerized) - window_size + 1):
                outs = numerized[idx : idx + window_size]
                yield Series(input=inps, output=outs)
                inps = outs

    def numerize(self, dataset: Iterable[T]) -> List[int]:
        """
        Replace values in iterable with corresponding number values.

        >>> numeris = Numeris(["abcdefg"])
        >>> numeris.numerize(["a", "b", "c"])
        [0, 1, 2]
        """
        mapping: Dict[T, int] = {}
        for x in sorted(set(dataset)):
            mapping.setdefault(x, len(mapping))

        return [mapping[x] for x in dataset]


class Series(NamedTuple):
    """A single series of data containing input/output values"""

    input: List[int]
    output: List[int]
