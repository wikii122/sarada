"""
Simple utility for dataset manipulations and storage.
"""
from __future__ import annotations

from typing import (
    Dict,
    Final,
    Generic,
    Iterable,
    Iterator,
    List,
    Mapping,
    NamedTuple,
    Tuple,
    TypeVar,
)

from loguru import logger

T = TypeVar("T")  # pylint: disable=invalid-name

Dataset = Tuple[Tuple[T, ...], ...]


class Numeris(Generic[T]):
    """
    Keep order of numeric data and allows to perform operation on those.

    Most notably allows to change values back and forth into ordered numerics.
    """

    def __init__(self, data: List[List[T]]):
        self.data: Final[Dataset[T]] = tuple(tuple(d) for d in data)
        mapping: Dict[T, int] = {}
        reverse_mapping: Dict[int, T] = {}

        for dataset in self.data:
            for key in dataset:
                mapping.setdefault(key, len(mapping))
                reverse_mapping.setdefault(mapping[key], key)

        self.mapping: Final[Mapping[T, int]] = mapping
        self.reverse_mapping: Final[Mapping[int, T]] = reverse_mapping

        logger.debug("Found {size} distinct values", size=self.distinct_size)

    def make_series(self, window_size: int = 100) -> Iterator[Series]:
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
        Series(input=[0.0, 0.25, 0.5], output=[0, 0, 0, 1, 0])

        >>> next(series)
        Series(input=[0.25, 0.5, 0.75], output=[0, 0, 0, 0, 1])

        >>> next(series)
        Traceback (most recent call last):
            ...
        StopIteration
        """
        processed = 0
        ommited = 0
        for dataset in self.data:
            numerized = self.numerize(dataset)
            idx = 0
            for idx in range(0, len(numerized) - window_size):
                ins = numerized[idx : idx + window_size]
                out = self.categorize(dataset[idx + window_size])
                yield Series(input=ins, output=out)

                processed += 1

            if idx:
                logger.debug(
                    "Current dataset yielded {num} series, moving to next", num=idx
                )
            else:
                ommited += 1
                logger.debug(
                    "Dataset of size {size} too short, ommiting", size=len(numerized)
                )

        logger.info("Yielded {num} series of data total", num=processed)
        if ommited:
            logger.warning("Dataset were ommited: {num} in total", num=ommited)

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
        values = [self.denormalize_value(x) for x in numerized]

        logger.debug("Denumerized list of {length} values", length=len(values))

        return values

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

    def categorize(self, val: T) -> List[int]:
        """
        Return array with zeroes and 1 on position marking value.

        >>> numeris = Numeris(["abcde"])
        >>> numeris.categorize("a")
        [1, 0, 0, 0, 0]
        """
        array = [0] * (self.distinct_size)
        array[self.mapping[val]] = 1

        return array

    def decategorize(self, val: List[int]) -> T:
        """
        Return normalized value to original.

        >>> numeris = Numeris(["abcde"])
        >>> numeris.decategorize([0, 1, 0, 0, 0])
        'b'
        """
        searched = max(val)
        idx = val.index(searched)

        return self.reverse_mapping[idx]

    @property
    def distinct_size(self) -> int:
        """
        Count number of distinct values in datasets.
        """
        return len(self.mapping)


class Series(NamedTuple):
    """A single series of data containing input/output values."""

    input: List[float]
    output: List[int]
