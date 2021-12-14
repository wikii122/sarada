from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from hypothesis import given
from hypothesis.strategies import from_type

from sarada.console import config


@given(from_type(config.ConfigData))
def test_config_store_load(cfg: config.ConfigData) -> None:
    with TemporaryDirectory() as temp:
        path = Path(temp)
        config.store(cfg, path)
        loaded = config.read(path)

    assert loaded == cfg
