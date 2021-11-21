from typing import List

from hypothesis import assume, given
from hypothesis.strategies import integers, lists

from sarada.neuron import prepare_dataset
from sarada.numeris import Numeris


@given(lists(lists(integers(), min_size=11), min_size=1))
def test_numeris_preare_dataset_keeps_data_length(texts: List[List[int]]) -> None:
    numeris = Numeris(texts)
    assume(numeris.data)

    series = list(numeris.make_series(window_size=10))

    ins, outs = prepare_dataset(series)

    assert len(ins) == len(series)
    assert len(outs) == len(series)
