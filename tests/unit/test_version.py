"""Tests for the package version."""

import re

from ramr import __version__


def test_version_follows_semantic_versioning() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)
