from typing import List

from hypothesis import assume, given
from hypothesis.strategies import SearchStrategy, data, integers, lists, text

from sarada.numeris import Numeris


@given(lists(lists(text(max_size=3)), max_size=2), data())
def test_numeris_series_generation_generates_desired_len(
    texts: List[List[str]], data: SearchStrategy
) -> None:
    max_size = max(len(s) for s in texts) if texts else 0
    size: int = data.draw(integers(min_value=1, max_value=max_size)) if max_size else 1

    numeris = Numeris(texts)
    series = numeris.make_series(window_size=size)

    lines = list(series)

    for line in lines:
        assert len(line.input) == size


@given(
    size=integers(min_value=10),
    texts=lists(lists(text(max_size=3), max_size=9)),
)
def test_numeris_series_generation_drops_too_short(
    size: int, texts: List[List[str]]
) -> None:
    numeris = Numeris(texts)
    series = numeris.make_series(window_size=size)

    lines = list(series)
    assert not lines


@given(lists(lists(text(max_size=3)), min_size=1, max_size=1), data())
def test_numeris_series_generation_outputs_length(
    texts: List[List[str]], data: SearchStrategy
) -> None:
    """
    Check if input of last item is shifted by one in next input.

    Predicate should hold only for single series on input.
    """
    max_size = max(len(s) for s in texts) if texts else 0
    size: int = data.draw(integers(min_value=1, max_value=max_size)) if max_size else 1

    numeris = Numeris(texts)
    series = numeris.make_series(window_size=size)

    for line in series:
        assert len(line.output) == numeris.distinct_size


@given(lists(lists(text(max_size=3)), min_size=1, max_size=1), data())
def test_numeris_series_generation_outputs_binary(
    texts: List[List[str]], data: SearchStrategy
) -> None:
    """
    Check if input of last item is shifted by one in next input.

    Predicate should hold only for single series on input.
    """
    max_size = max(len(s) for s in texts) if texts else 0
    size: int = data.draw(integers(min_value=1, max_value=max_size)) if max_size else 1

    numeris = Numeris(texts)
    series = numeris.make_series(window_size=size)

    for line in series:
        assert sum(line.output) == 1
        assert 1 <= len(set(line.output)) <= 2
        assert 1 in line.output


@given(lists(lists(text(max_size=3)), max_size=5))
def test_numeris_numerize_returns_numbers(texts: List[List[str]]) -> None:
    numeris = Numeris(texts)
    assume(numeris.data)
    numerized = numeris.numerize(numeris.data[0])

    assert all(isinstance(num, float) for num in numerized)


@given(lists(lists(text(max_size=3)), max_size=5))
def test_numeris_numerize_is_reversable(texts: List[List[str]]) -> None:
    numeris = Numeris(texts)
    assume(numeris.data)
    data = list(numeris.data[0])

    assert numeris.denumerize(numeris.numerize(data)) == data


@given(lists(lists(text(max_size=3)), max_size=5))
def test_numeris_normalize_is_reversable(texts: List[List[str]]) -> None:
    numeris = Numeris(texts)
    assume(numeris.data)
    data = numeris.mapping.keys()

    assert all(numeris.denormalize_value(numeris.normalize_value(x)) == x for x in data)


@given(lists(lists(text(max_size=3)), max_size=5))
def test_numeris_categorize_is_reversable(texts: List[List[str]]) -> None:
    numeris = Numeris(texts)
    assume(numeris.data)
    data = numeris.mapping.keys()

    assert all(numeris.decategorize(numeris.categorize(x)) == x for x in data)


@given(lists(lists(text(max_size=3)), max_size=5))
def test_numeris_normalize_normalizes(texts: List[List[str]]) -> None:
    numeris = Numeris(texts)
    assume(numeris.data)
    data = numeris.mapping.keys()

    assert all(0 <= numeris.normalize_value(x) <= 1 for x in data)
