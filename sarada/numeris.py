"""
Simple utility for dataset manipulations and storage.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generator, Generic, List, Tuple, TypeVar

T = TypeVar("T")

Dataset = Tuple[Tuple[T, ...], ...]


class Numeris(Generic[T]):
    """
    Keep order of numeric data and allows to perform operation on those.

    Most notably allows to change values back and forth into ordered numerics.
    """

    def __init__(self, data: List[List[T]]):
        self.data: Dataset = tuple(tuple(d) for d in data)

    def make_series(self, window_size: int = 100) -> Generator[Series, None, None]:
        """
        Generate series of overlapping datasets from data using crawling windows.

        Resulting data will contain input and output where output will be input shifted
        by one. For instance "abcdefg" with window size 5 will generate 2 datasets, one
        with input 'abcde' and output 'bcdef' and second with input 'bcdef' and output
        'cdefg'.

        >>> numeris = Numeris(["abcdefg"])
        >>> series = numeris.make_series(window_size=5)

        >>> next(series)
        Series(input=('a', 'b', 'c', 'd', 'e'), output=('b', 'c', 'd', 'e', 'f'))

        >>> next(series)
        Series(input=('b', 'c', 'd', 'e', 'f'), output=('c', 'd', 'e', 'f', 'g'))

        >>> next(series)
        Traceback (most recent call last):
            ...
        StopIteration
        """

        for dataset in self.data:
            inps = dataset[:window_size]
            for idx in range(1, len(dataset) - window_size + 1):
                outs = dataset[idx : idx + window_size]
                yield Series(input=inps, output=outs)
                inps = outs


@dataclass(frozen=True)
class Series(Generic[T]):
    """A single series of data containing input/output values"""

    __slots__ = "input", "output"

    input: Tuple[T, ...]
    output: Tuple[T, ...]
