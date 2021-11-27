from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import pytest

from hypothesis import assume, given, settings
from hypothesis.strategies import integers, lists

from sarada.neuron import Neuron
from sarada.numeris import Numeris


@given(lists(lists(integers(), min_size=11), min_size=1))
def test__prepare_dataset_keeps_data_length(texts: List[List[int]]) -> None:
    windows_size = 10

    numeris = Numeris(texts)
    assume(numeris.data)

    neuron = Neuron(windows_size, numeris.distinct_size)

    series = list(numeris.make_series(window_size=windows_size))

    ins, outs = neuron.prepare_dataset(series)

    assert len(ins) == len(series)
    assert len(outs) == len(series)


@given(
    integers(min_value=1, max_value=500),
    integers(min_value=1, max_value=500),
)
@settings(max_examples=5, deadline=None)
def test_make_model(x: int, y: int) -> None:
    neuron = Neuron(x, y)

    assert neuron.model.input_shape[1] == x
    assert neuron.model.output_shape[1] == y


@given(
    integers(min_value=1, max_value=100),
    integers(min_value=1, max_value=100),
    integers(min_value=1, max_value=100),
)
@settings(max_examples=2, deadline=None)
def test_generate_return_wanted_length(x: int, y: int, z: int) -> None:
    neuron = Neuron(x, y)

    seq = neuron.generate(z)

    assert len(seq) == z


def test_load_save() -> None:
    neuron = Neuron(3, 4)

    with TemporaryDirectory() as tmp_path:
        path = Path(tmp_path) / "object"
        neuron.save(path)

        loaded = Neuron.load(path, 3, 4)

        cmp = (
            x == y
            for x, y in zip(neuron.model.get_weights(), loaded.model.get_weights())
        )
        assert (c.all() for c in cmp)


def test_check_save_size() -> None:
    neuron = Neuron(3, 4)

    with TemporaryDirectory() as tmp_path:
        path = Path(tmp_path) / "object"
        neuron.save(path)

        with pytest.raises(ValueError):
            Neuron.load(path, 2, 4)
