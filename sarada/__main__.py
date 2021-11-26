"""
Allow executing module as a command.
"""
from __future__ import annotations

import typer

from sarada.app import main

if __name__ == "__main__":
    typer.run(main)
