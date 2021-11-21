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
    Mapping,
    NamedTuple,
    Tuple,
    TypeVar,
)

T = TypeVar("T")  # pylint: disable=invalid-name

Dataset = Tuple[Tuple[T, ...], ...]


class Numeris(Generic[T]):
    """
    Keep order of numeric data and allows to perform operation on those.

    Most notably allows to change values back and forth into ordered numerics.
    """

    def __init__(self, data: List[List[T]]):
        self.data: Final[Dataset] = tuple(tuple(d) for d in data)
        mapping: Dict[T, int] = {}
        reverse_mapping: Dict[int, T] = {}

        for dataset in self.data:
            for key in dataset:
                mapping.setdefault(key, len(mapping))
                reverse_mapping.setdefault(mapping[key], key)

        self.mapping: Final[Mapping[T, int]] = mapping
        self.reverse_mapping: Final[Mapping[int, T]] = reverse_mapping

    def make_series(self, window_size: int = 100) -> Generator[Series, None, None]:
        """
        Generate series of overlapping datasets from data using crawling windows.

        Resulting data will contain input and output where output will be input shifted
        by one. For instance "abcdefg" with window size 5 will generate 2 datasets, one
        with input 'abcde' and output 'bcdef' and second with input 'bcdef' and output
        'cdefg'. Then it replaces these values with ordered numeric values using
        numerization functions and normalizes them.

        >>> numeris = Numeris(["abcde"])
        >>> series = numeris.make_series(window_size=3)

        >>> next(series)
        Series(input=[0.0, 0.25, 0.5], output=0.75)

        >>> next(series)
        Series(input=[0.25, 0.5, 0.75], output=1.0)

        >>> next(series)
        Traceback (most recent call last):
            ...
        StopIteration
        """
        for dataset in self.data:
            numerized = self.numerize(dataset)
            for idx in range(0, len(numerized) - window_size):
                inps = numerized[idx : idx + window_size]
                yield Series(input=inps, output=numerized[idx + window_size])

    def numerize(self, dataset: Iterable[T]) -> List[float]:
        """
        Replace values in iterable with corresponding normalized number values.

        >>> numeris = Numeris(["abcde"])
        >>> numeris.numerize(["a", "b", "c", "d", "e"])
        [0.0, 0.25, 0.5, 0.75, 1.0]
        """
        return [self.normalize_value(x) for x in dataset]

    def denumerize(self, numerized: Iterable[float]) -> List[T]:
        """
        Replace values in iterable containing normalized dataset with original values.

        >>> numeris = Numeris(["abcde"])
        >>> numeris.denumerize([0.0, 0.25, 0.5])
        ['a', 'b', 'c']
        """
        return [self.denormalize_value(x) for x in numerized]

    def normalize_value(self, value: T) -> float:
        """
        Return normalized values for a given value.

        >>> numeris = Numeris(["abcde"])
        >>> numeris.normalize_value("a")
        0.0

        >>> numeris.normalize_value("b")
        0.25
        """
        numeric = self.mapping[value]
        if self.distinct_size == 1:
            return 0.0  # Zero division otherwise

        return numeric / (self.distinct_size - 1)

    def denormalize_value(self, val: float) -> T:
        """
        Return normalized value to original.

        >>> numeris = Numeris(["abcde"])
        >>> numeris.denormalize_value(0.25)
        'b'
        """
        # Denormalize and round value to nearest int
        key = int(val * (self.distinct_size - 1) + 0.5)

        return self.reverse_mapping[key]

    @property
    def distinct_size(self) -> int:
        """
        Count number of distinct values in datasets.
        """
        return len(self.mapping)


class Series(NamedTuple):
    """A single series of data containing input/output values."""

    input: List[float]
    output: float
