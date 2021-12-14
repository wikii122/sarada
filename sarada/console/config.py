"""
Configuration for model.
"""
from __future__ import annotations

import json

from pathlib import Path
from typing import TypedDict

filename = "config.json"


class ConfigData(TypedDict):
    iterations: int


def read(path: Path) -> ConfigData:
    with open(path / filename, "r", encoding="utf-8") as datafile:
        data: ConfigData = json.load(datafile)

    return data


def store(data: ConfigData, path: Path) -> None:
    with open(path / filename, "w", encoding="utf-8") as datafile:
        json.dump(data, datafile)
