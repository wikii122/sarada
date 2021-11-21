from typing import List

from hypothesis import assume, given, settings
from hypothesis.strategies import integers, lists

from sarada.neuron import assemble_model, prepare_dataset
from sarada.numeris import Numeris


@given(lists(lists(integers(), min_size=11), min_size=1))
def test__prepare_dataset_keeps_data_length(texts: List[List[int]]) -> None:
    numeris = Numeris(texts)
    assume(numeris.data)

    series = list(numeris.make_series(window_size=10))

    ins, outs = prepare_dataset(series)

    assert len(ins) == len(series)
    assert len(outs) == len(series)


@given(
    integers(min_value=1, max_value=100),
    integers(min_value=1, max_value=100),
    integers(min_value=1, max_value=100),
)
@settings(max_examples=5, deadline=1500)
def test_make_model(x: int, y: int, z: int) -> None:
    model = assemble_model((x, y, 1), z)

    assert model.output_shape[1] == z
    print(x, y, z, model.input_shape)
    assert model.input_shape[1] == y
